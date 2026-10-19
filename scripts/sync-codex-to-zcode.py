#!/usr/bin/env python3
"""codex -> zcode 用户级配置每日同步（幂等）。

同步范围：~/.codex 的 AGENTS.md、rules/*.md、skills、hooks、agents
落点：~/.zcode/AGENTS.md、~/.zcode/rules/、~/.agents/skills/、~/.zcode/hooks/ + ~/.zcode/v2/config.json、~/.zcode/agents/

内置适配（codex 专有特性按 zcode 能力改写，不做无脑复制）：
- AGENTS.md §0 新对话标题提炼：依赖 Codex 内置 set_thread_title，ZCode 无等价工具 → 整节标注「Codex 专用，ZCode 跳过」
- 所有 ~/.codex/ 路径引用 → ~/.zcode/（含 ~/.Codex 大小写变体、.codex/rules 相对写法）
- 「rules 自动加载」表述 → ZCode 不自动加载，须按引用主动读取
- agents：Codex TOML（sandbox_mode=read-only）→ ZCode markdown/frontmatter，只读审计映射 tools: [Read, Bash]
- hooks：脚本原样复制（本身是工具无关的 file_path 解析）；hooks 配置从 ~/.codex/hooks.json 通用转换
  （zcode 七类事件白名单、脚本路径改写、matcher 保留），以 hooks.events 结构 + enabled:true 写入
  ~/.zcode/cli/config.json；hooks.json 缺失或无法解析时回退到已知两钩子并报警
- MCP：~/.codex/config.toml [mcp_servers.*] → ~/.zcode/cli/config.json 的 mcp.servers 及 ~/.agents/mcp.json 的 mcpServers；
  Codex 内置运行时类 server（如 node_repl，命令/环境变量指向 Codex 安装目录）判定为 Codex 专用并跳过；
  startup_timeout_sec 在 zcode 无对应字段，丢弃
- skills：按文件 mtime 较新者同步，zcode 侧较新的同名文件不会被 codex 旧版覆盖；
  hatch-pet（依赖 Codex 内置 $imagegen、load_workspace_dependencies、CODEX_HOME pets）判定为 Codex 专用并跳过

脚本发现无法内置适配的新 codex 专有特性时输出 WARNING，由执行的代理做语义适配。
"""
import json
import re
import shutil
import tomllib
from pathlib import Path

HOME = Path.home()
CODEX = HOME / '.codex'
Z = HOME / '.zcode'
ASKILLS = HOME / '.agents' / 'skills'
CFG = Z / 'cli' / 'config.json'

report, warns = [], []


def note(m):
    report.append(m)


def warn(m):
    warns.append(m)


PATH_SUBS = [
    (re.compile(r'~/\.codex/', re.I), '~/.zcode/'),
    (re.compile(r'\.codex/rules/'), '.zcode/rules/'),
]


def rewrite_paths(t):
    for rx, rep in PATH_SUBS:
        t = rx.sub(rep, t)
    return t


# ---------- 1. AGENTS.md ----------
src = (CODEX / 'AGENTS.md').read_text(encoding='utf-8')
t = rewrite_paths(src)

SEC0 = re.compile(r'## 0\.[^\n]*\n(?:(?!^## |^---).*\n?)*', re.M)
Z0 = """## 0. 新对话标题自动提炼（Codex 专用，ZCode 跳过）

- 本规则依赖 Codex 运行时内置的 `set_thread_title` 工具；ZCode 未提供等价的会话标题设置工具，本节在 ZCode 环境下整体跳过，不产生任何动作。
- 若未来 ZCode 提供等价工具，可恢复为：根据首条用户消息提炼不超过 30 个字符的中文短标题并设置；用户显式要求保留/自定义当前标题时除外。
"""
t2, n = SEC0.subn(Z0, t, count=1)
if n:
    t = t2
else:
    warn('AGENTS.md: 未定位到 §0 标题提炼章节，请人工核查 set_thread_title 相关内容')

t = re.sub(r'rules 规则文件（`?~/\.zcode/rules/`?）自动加载',
           'rules 规则文件（`~/.zcode/rules/`）不会自动加载，命中场景时须先主动读取对应文件', t)
residual = [ln.strip()[:80] for ln in t.splitlines() if '自动加载' in ln and '不会' not in ln]
if residual:
    warn('AGENTS.md: 疑似残留「rules 自动加载」表述: ' + ' | '.join(residual))

if 'ZCode 适配说明' not in t:
    t = re.sub(r'(本文件是全局最高优先级协作准则[^\n]*\n)',
               r'\1> ZCode 适配说明：ZCode 不会像 Codex 一样自动加载 `rules/*.md`；命中下方引用的规则场景时，必须先读取对应规则文件再执行。\n',
               t, count=1)

dst = Z / 'AGENTS.md'
if not dst.exists() or dst.read_text(encoding='utf-8') != t:
    dst.write_text(t, encoding='utf-8')
    note('AGENTS.md → ~/.zcode/AGENTS.md（路径改写 + §0 标题提炼适配 + 自动加载表述适配）')
else:
    note('AGENTS.md: 无变化')

for line in t.splitlines():
    if 'set_thread_title' in line and 'Codex' not in line and 'ZCode' not in line:
        warn(f'AGENTS.md 残留 set_thread_title 引用: {line.strip()[:80]}')

# ---------- 2. rules/*.md ----------
rdir = Z / 'rules'
rdir.mkdir(parents=True, exist_ok=True)
changed = []
for f in sorted((CODEX / 'rules').glob('*.md')):
    t = rewrite_paths(f.read_text(encoding='utf-8'))
    d = rdir / f.name
    if not d.exists() or d.read_text(encoding='utf-8') != t:
        d.write_text(t, encoding='utf-8')
        changed.append(f.name)
note('rules → ~/.zcode/rules: 更新 ' + (', '.join(changed) if changed else '无（内容一致）'))
left = [p.name for p in rdir.glob('*.md') if re.search(r'\.codex/', p.read_text(encoding='utf-8'))]
if left:
    warn('rules 残留 .codex 路径引用: ' + ', '.join(left))

# ---------- 3. skills（较新者胜出） ----------
SKILL_SKIP = {'hatch-pet'}


def sync_skills():
    synced = kept = same = 0
    kept_by = {}
    for sd in sorted((CODEX / 'skills').iterdir()):
        if not sd.is_dir() or sd.name.startswith('.'):
            continue
        if sd.name in SKILL_SKIP:
            warn(f'skills: 跳过 {sd.name}（依赖 Codex 内置 $imagegen / load_workspace_dependencies / '
                 f'CODEX_HOME pets 基础设施，ZCode 无等价能力，标记「Codex 专用」）')
            continue
        td = ASKILLS / sd.name
        for f in sd.rglob('*'):
            if not f.is_file():
                continue
            tf = td / f.relative_to(sd)
            if not tf.exists() or f.stat().st_mtime > tf.stat().st_mtime:
                tf.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, tf)
                synced += 1
            elif f.read_bytes() == tf.read_bytes():
                same += 1
            else:
                kept += 1
                kept_by.setdefault(sd.name, 0)
                kept_by[sd.name] += 1
    kept_desc = '; '.join(f'{k}({v})' for k, v in sorted(kept_by.items())) or '-'
    note(f'skills → ~/.agents/skills: 复制 {synced} 个文件（codex 较新/新增），'
         f'跳过技能 {len(SKILL_SKIP)} 个，保留 zcode 较新 {kept} 个（{kept_desc}），一致 {same} 个')


# hatch-pet 是 Codex 专属宠物孵化技能，同步产物一次性清理
stale_hatch = ASKILLS / 'hatch-pet'
if stale_hatch.exists():
    shutil.rmtree(stale_hatch)
    note('skills: 移除 hatch-pet（Codex 专用技能，不适用于 zcode）')
sync_skills()
synced = kept = same = None

# ---------- 4. hooks ----------
hdir = Z / 'hooks'
hdir.mkdir(parents=True, exist_ok=True)
hchanged = []
for f in (CODEX / 'hooks').glob('*.js'):
    d = hdir / f.name
    if not d.exists() or d.read_bytes() != f.read_bytes():
        shutil.copy2(f, d)
        hchanged.append(f.name)
note('hooks 脚本 → ~/.zcode/hooks: ' + (', '.join(hchanged) if hchanged else '无变化'))

ZCODE_EVENTS = {'SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PermissionRequest',
                'PostToolUse', 'PostToolUseFailure', 'Stop'}
HOOK_SCRIPT_RX = re.compile(r'hooks[\\/]+([\w.-]+\.js)', re.I)


def build_hooks_cfg():
    """从 ~/.codex/hooks.json 通用转换；缺失或无法解析时回退到内置已知两钩子。"""
    try:
        data = json.loads((CODEX / 'hooks.json').read_text(encoding='utf-8'))
        events = {}
        for ev, entries in (data.get('hooks') or {}).items():
            if ev not in ZCODE_EVENTS:
                warn(f'hooks: 事件 {ev} 不在 zcode 支持的七类事件内，跳过')
                continue
            conv = []
            for entry in entries or []:
                hs = []
                for h in (entry or {}).get('hooks') or []:
                    m = HOOK_SCRIPT_RX.search(h.get('command', ''))
                    if h.get('type') != 'command' or not m:
                        warn(f'hooks: {ev} 存在无法转换的条目（非 command 或未引用 hooks/*.js），已跳过')
                        continue
                    hs.append({'type': 'command',
                               'command': f'node "{(hdir / m.group(1)).as_posix()}"'})
                if hs:
                    e = {'hooks': hs}
                    if (entry or {}).get('matcher'):
                        e['matcher'] = entry['matcher']
                    conv.append(e)
            if conv:
                events[ev] = conv
        if events:
            return {'enabled': True, 'events': events}
        warn('hooks.json 无可转换条目，回退到内置已知钩子')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        warn(f'读取 ~/.codex/hooks.json 失败（{e}），回退到内置已知钩子')
    fb = lambda name: f'node "{(hdir / name).as_posix()}"'
    return {'enabled': True, 'events': {
        'PreToolUse': [{'matcher': 'Edit|Write|MultiEdit',
                        'hooks': [{'type': 'command', 'command': fb('guard-config-edit.js')}]}],
        'PostToolUse': [{'matcher': 'Edit|Write|MultiEdit',
                         'hooks': [{'type': 'command', 'command': fb('vue-parse-check.js')}]}],
    }}


hooks_cfg = build_hooks_cfg()
cfg = json.loads(CFG.read_text(encoding='utf-8')) if CFG.exists() else {}
if cfg.get('hooks') != hooks_cfg:
    if CFG.exists():
        shutil.copy2(CFG, CFG.with_suffix('.json.sync-bak'))
    cfg['hooks'] = hooks_cfg
    CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    note(f'hooks 配置写入 {CFG}（hooks.events 结构，enabled=true，已备份 .sync-bak）')
else:
    note('hooks 配置: 无变化')

# ---------- 5. agents（TOML → markdown frontmatter） ----------
adir = Z / 'agents'
adir.mkdir(parents=True, exist_ok=True)
a_changed = []
for f in sorted((CODEX / 'agents').glob('*.toml')):
    data = tomllib.loads(f.read_text(encoding='utf-8'))
    name = data.get('name') or f.stem
    desc = (data.get('description') or '').replace('\\', '\\\\').replace('"', '\\"')
    body = rewrite_paths(data.get('developer_instructions') or '')
    tools = '[Read, Bash]' if data.get('sandbox_mode') == 'read-only' else '[Read, Bash, Edit, Write]'
    md = f"---\nname: {name}\ndescription: \"{desc}\"\ntools: {tools}\n---\n\n{body}\n"
    d = adir / (f.stem + '.md')
    if not d.exists() or d.read_text(encoding='utf-8') != md:
        d.write_text(md, encoding='utf-8')
        a_changed.append(d.name)
note('agents (TOML→markdown) → ~/.zcode/agents: ' + (', '.join(a_changed) if a_changed else '无变化'))

# ---------- 6. MCP ----------
MCP_STATE = Path(__file__).with_name('sync-mcp-state.json')
CODEX_INTERNAL_RX = re.compile(r'(openai[\\/]+codex|[\\/]\.codex|codex_home|codex_cli_path|codex-computer-use)', re.I)


def _rw(s):
    return re.sub(r'\.codex(?=[\\/]|$)', '.zcode', s, flags=re.I)


codex_mcp = {}
mcp_parsed = False
try:
    cx = tomllib.loads((CODEX / 'config.toml').read_text(encoding='utf-8'))
    mcp_parsed = True
    for name, d in (cx.get('mcp_servers') or {}).items():
        if not isinstance(d, dict) or not d:
            continue
        if CODEX_INTERNAL_RX.search(json.dumps(d, ensure_ascii=False)):
            note(f'MCP: 跳过 {name}（Codex 内置运行时，ZCode 自有等价能力）')
            continue
        if d.get('url'):
            zc = {'type': 'http', 'url': _rw(d['url'])}
            if d.get('bearer_token_env_var'):
                warn(f'MCP {name}: url 型服务的 bearer_token_env_var 需人工适配为 zcode headers 鉴权')
        else:
            zc = {'type': 'stdio', 'command': _rw(d.get('command', ''))}
            if d.get('args'):
                zc['args'] = [_rw(a) if isinstance(a, str) else a for a in d['args']]
            env = {k: _rw(v) for k, v in (d.get('env') or {}).items() if isinstance(v, str)}
            if env:
                zc['env'] = env
        codex_mcp[name] = zc
except (FileNotFoundError, tomllib.TOMLDecodeError) as e:
    warn(f'读取 ~/.codex/config.toml 失败（{e}），本次跳过 MCP 同步')

if mcp_parsed:
    cfg = json.loads(CFG.read_text(encoding='utf-8')) if CFG.exists() else {}
    zc_mcp = dict((cfg.get('mcp') or {}).get('servers') or {})
    managed_old = set(json.loads(MCP_STATE.read_text(encoding='utf-8'))['managed']) if MCP_STATE.exists() else set()
    removed = sorted(n for n in managed_old if n not in codex_mcp)
    for n in removed:
        zc_mcp.pop(n, None)
        warn(f'MCP: {n} 已从 codex 移除，同步删除 zcode 侧配置')
    zc_mcp.update(codex_mcp)
    managed = (managed_old & set(zc_mcp)) | set(codex_mcp)
    zc_only = sorted(n for n in zc_mcp if n not in managed)
    if zc_only:
        note('MCP: zcode 侧独立配置（不改动）: ' + ', '.join(zc_only))
    if cfg.get('mcp', {}).get('servers') != zc_mcp:
        if CFG.exists():
            shutil.copy2(CFG, CFG.with_suffix('.json.sync-bak'))
        cfg.setdefault('mcp', {})['servers'] = zc_mcp
        CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
        note(f'MCP servers 写入 {CFG}（mcp.servers，{len(zc_mcp)} 个，已备份 .sync-bak）')
    else:
        note('MCP (cli config): 无变化')
    fj = HOME / '.agents' / 'mcp.json'
    fj_content = {'mcpServers': zc_mcp}
    if not fj.exists() or json.loads(fj.read_text(encoding='utf-8')) != fj_content:
        fj.parent.mkdir(parents=True, exist_ok=True)
        fj.write_text(json.dumps(fj_content, ensure_ascii=False, indent=2), encoding='utf-8')
        note(f'MCP servers 写入 {fj}（mcpServers 兼容回退，{len(zc_mcp)} 个）')
    else:
        note('MCP (.agents/mcp.json): 无变化')
    MCP_STATE.write_text(json.dumps({'managed': sorted(managed)}, ensure_ascii=False), encoding='utf-8')

# ---------- 7. 校验与报告 ----------
def leftover_refs(p):
    try:
        return len(re.findall(r'\.codex/', p.read_text(encoding='utf-8')))
    except OSError:
        return -1

la = leftover_refs(Z / 'AGENTS.md')
note(f'校验: ~/.zcode/AGENTS.md 残留 .codex 路径引用 {la} 处')
if la:
    warn('AGENTS.md 仍有 .codex 路径引用，需人工适配')

print('=== 同步报告 ===')
for m in report:
    print(' -', m)
if warns:
    print('=== WARNING（需按 zcode 能力做语义适配）===')
    for w in warns:
        print(' !', w)
else:
    print('WARNING: 无')
