<div align="center">

# 🧩 zcode-si

### ZCode 用户级配置完整备份 & 迁移指南

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Skills](https://img.shields.io/badge/skills-8-8A2BE2)
![Rules](https://img.shields.io/badge/rules-11-green)
![Agents](https://img.shields.io/badge/agents-2-orange)
![Hooks](https://img.shields.io/badge/hooks-2-red)
![MCP](https://img.shields.io/badge/MCP_servers-4-ff69b4)

**一份可以直接交给任何人 / 任何 AI 助手，照着做就能 1:1 复刻的 ZCode 配置。**

</div>

> [!NOTE]
> 本仓库是 [ZCode](https://zcode.dev)（AI 编码桌面助手）的**用户级配置备份**，包含全局协作准则 `AGENTS.md`、11 个 `rules` 专项规则、8 个 `skills` 技能、2 个只读审计 `agents`、2 个 `hooks` 钩子，以及 4 个 `MCP` 服务器与插件配置。
>
> 无论你是**手动迁移**，还是把本 README 丢给 **Claude / ChatGPT / Cursor / ZCode 自己**，按本文步骤执行，都可以在新机器上完整复现这套配置。

---

## 📑 目录

- [🏗️ 仓库结构总览](#-仓库结构总览)
- [⚙️ 前置条件](#-前置条件)
- [🚀 快速开始（AI 一键迁移）](#-快速开始ai-一键迁移)
- [🤖 AI 迁移提示词模板](#-ai-迁移提示词模板)
- [🧭 手动迁移详解（分步）](#-手动迁移详解分步)
  - [Step 0 · 备份现有配置](#step-0--备份现有配置)
  - [Step 1 · 克隆本仓库](#step-1--克隆本仓库)
  - [Step 2 · 安装 AGENTS.md（全局最高优先级准则）](#step-2--安装-agentsmd全局最高优先级准则)
  - [Step 3 · 安装 rules（11 个专项规则）](#step-3--安装-rules11-个专项规则)
  - [Step 4 · 安装 skills（8 个技能）](#step-4--安装-skills8-个技能)
  - [Step 5 · 安装 agents（2 个只读审计子代理）](#step-5--安装-agents2-个只读审计子代理)
  - [Step 6 · 安装 hooks（2 个钩子脚本）](#step-6--安装-hooks2-个钩子脚本)
  - [Step 7 · 配置 cli/config.json（hooks 注册 + MCP + 插件）](#step-7--配置-cliconfigjsonhooks-注册--mcp--插件)
  - [Step 8 · 重启并验证](#step-8--重启并验证)
- [🧩 Skills 使用详解（怎么触发、怎么用）](#-skills-使用详解怎么触发怎么用)
- [🪝 Hooks 详解](#-hooks-详解)
- [🔌 MCP 服务器详解](#-mcp-服务器详解)
- [👥 自定义 Agents 详解](#-自定义-agents-详解)
- [📜 Rules 规则速查表](#-rules-规则速查表)
- [❓ FAQ 故障排查](#-faq-故障排查)
- [🔐 安全与隐私](#-安全与隐私)
- [✅ 迁移完成检查清单](#-迁移完成检查清单)

---

## 🏗️ 仓库结构总览

```text
zcode-si/
├── AGENTS.md                        # 🌟 全局最高优先级协作准则（ZCode 启动即读取）
├── README.md                        # 📖 本文档
├── .gitattributes                   # Git 换行符标准化（text=auto, LF）
│
├── rules/                           # 📜 11 个专项规则（按需被 AGENTS.md 引用读取）
│   ├── annotation.md                #    业务注释强制规则（六要素 / A-B-C-R 档）
│   ├── business-assumptions.md      #    业务假设与数据验证规范
│   ├── delivery.md                  #    交付结构模板（标准 / 简化交付）
│   ├── design-principles.md         #    设计模式与组件化决策边界
│   ├── engineering-core.md          #    工程核心规范（安全 / 持久层 / 性能）
│   ├── frontend.md                  #    前端工程规范
│   ├── pitfalls.md                  #    后端 / 前端 / 历史项目高频陷阱
│   ├── response-quality.md          #    回复质量规范（事实证据 / 行动导向）
│   ├── subagent.md                  #    Subagent 约束
│   ├── version-control.md           #    版本控制纪律（Git 只读白名单等）
│   └── workflows.md                 #    开发工作流路由 + 修改后影响面审查
│
├── skills/                          # 🧩 8 个技能（每个目录含 SKILL.md + frontmatter）
│   ├── archify/                     #    架构图 / 流程图 / 时序图生成器
│   ├── deep-brainstorming/          #    深度头脑风暴
│   ├── init-project/                #    项目初始化（生成 AGENTS.md 等项目指令文件）
│   ├── multi-end-align/             #    多端业务一致性对齐核验
│   ├── rules-doc-reviewer/          #    规则文档审查与优化
│   ├── shuorenhua/                  #    去 AI 味 / 审稿润色
│   ├── teach-me/                    #    AI 边教边做（含独立 install.js）
│   └── ui-design/                   #    UI 设计 / 布局方案对比
│
├── agents/                          # 👥 2 个只读审计子代理
│   ├── annotation-auditor.md        #    业务注释一致性审查（Read + Bash）
│   └── cross-end-auditor.md         #    多端业务一致性审计（Read + Bash）
│
├── hooks/                           # 🪝 2 个钩子脚本（Node.js）
│   ├── guard-config-edit.js         #    PreToolUse：application*.yml 编辑前阻断
│   └── vue-parse-check.js           #    PostToolUse：前端源码编辑后语法解析校验
│
└── cli/
    └── config.json                  # ⚙️ ZCode CLI 层配置：hooks 注册 + MCP 服务器 + 插件
```

> [!TIP]
> **配置分层逻辑**：`AGENTS.md` 是入口与最高优先级准则，它按场景**主动引用** `rules/*.md`；`skills` 承载按需执行的流程；`hooks` 是机制级强制（不依赖 AI 自觉）；`MCP` 提供外部工具能力。理解这一点，排查问题时就知道该看哪个文件。

---

## ⚙️ 前置条件

| 依赖 | 用途 | 必需性 | 备注 |
|------|------|--------|------|
| 🖥️ **ZCode 桌面版** | 运行本配置的主体 | ✅ 必需 | 从官方渠道安装最新版 |
| 🟢 **Node.js（建议 LTS ≥ 20）** | hooks 脚本执行 + MCP 服务器经 `npx` 启动 | ✅ 必需 | 安装后 `node -v`、`npx -v` 均可用 |
| 🔧 **Git** | 克隆本仓库 | ✅ 必需 | Git Bash 环境执行下述命令最顺 |

> [!IMPORTANT]
> 本教程命令默认在 **Git Bash / POSIX shell** 下执行，`~` 代表你的用户主目录：
> - **Windows**：`C:\Users\<你的用户名>\`，即 `%USERPROFILE%`
> - **macOS / Linux**：`/Users/<你>` 或 `/home/<你>`
>
> PowerShell 用户请把 `cp -r` 换成 `Copy-Item -Recurse`，`mkdir -p` 换成 `New-Item -ItemType Directory -Force`。

**本教程所有落点目录一览**（迁移目标）：

| 仓库内文件 | 安装落点（用户级） |
|------------|--------------------|
| `AGENTS.md` | `~/.zcode/AGENTS.md` |
| `rules/*.md` | `~/.zcode/rules/` |
| `skills/*` | `~/.zcode/skills/` |
| `agents/*.md` | `~/.zcode/agents/` |
| `hooks/*.js` | `~/.zcode/hooks/` |
| `cli/config.json` | 合并进 `~/.zcode/cli/config.json`（**不能整文件覆盖！**） |

---

## 🚀 快速开始（AI 一键迁移）

最快速的路线，三步搞定：

1. **克隆本仓库**到本地任意目录：
   ```bash
   git clone <本仓库地址> zcode-si
   cd zcode-si
   ```
2. **打开你的 AI 助手**（ZCode 新会话 / Claude / ChatGPT / Cursor 均可），把本文末尾 [🤖 AI 迁移提示词模板](#-ai-迁移提示词模板) 整段复制给它，并告诉它本仓库在你磁盘上的**绝对路径**。
3. AI 会自动完成：备份 → 拷贝 → 路径改写 → JSON 合并 → 输出验证清单。你只需要按它的提示**重启 ZCode** 并逐项确认。

> [!TIP]
> 让 **ZCode 自己**执行迁移效果最好——它有本地文件读写与命令执行能力，且能直接理解本 README 的语境。在 ZCode 里输入：`请阅读 <仓库路径>/README.md，按照其中的 AI 迁移提示词模板，把这套配置完整迁移到我的用户目录`。

---

## 🤖 AI 迁移提示词模板

把下面整段提示词复制给任意 AI 助手（配合本仓库路径使用）：

```text
你是一名系统配置迁移助手。请把「zcode-si」仓库中的 ZCode 用户级配置完整迁移到
我的机器上。请严格按以下步骤执行，每步先说明你要做什么再动手：

【仓库位置】<把本仓库的绝对路径填在这里，例如 F:\zcode-si>

【目标落点】（~ 代表我的用户主目录）
1. 仓库 AGENTS.md            → ~/.zcode/AGENTS.md
2. 仓库 rules/*.md（11 个）  → ~/.zcode/rules/
3. 仓库 skills/*（8 个目录） → ~/.zcode/skills/
4. 仓库 agents/*.md（2 个）  → ~/.zcode/agents/
5. 仓库 hooks/*.js（2 个）   → ~/.zcode/hooks/
6. 仓库 cli/config.json      → 合并进 ~/.zcode/cli/config.json（见合并规则）

【硬性规则】
A. 动手前先备份：把 ~/.zcode/cli/config.json 复制为 config.json.bak-<日期>；
   已存在的同名目标文件（AGENTS.md / rules / skills 等）也先备份到
   ~/.zcode/backup-<日期>/ 再覆盖。
B. cli/config.json 必须是「字段级合并」而不是整文件覆盖：只把仓库文件中的
   hooks（hooks.events 与 hooks.enabled）、mcp（mcp.servers）、
   plugins（plugins.enabledPlugins）三段合并进目标文件；目标文件里已有的
   其他字段一律保留原值。合并后用 JSON 解析器校验合法性。
C. hooks 注册的 command 里的脚本绝对路径必须改写为我的用户目录：
   把 "C:/Users/caixi/.zcode/hooks/guard-config-edit.js" 改成
   "C:/Users/<我的Windows用户名>/.zcode/hooks/guard-config-edit.js"，
   vue-parse-check.js 同理（保持正斜杠）。
D. plugins.enabledPlugins 中 "tc-experts@dev-tc-experts" 来自作者私有
   marketplace，我这里没有该源，请置为 false 或删除该行；其余三个官方
   插件（computer-use / github / claude-md-management）保留为 true。
E. 全程不要执行任何 git 写操作（commit / push / branch 等），只读克隆即可。
F. 每一步完成后输出简短进度：已完成项 / 阻塞项 / 下一步。

【完成后的验证清单】（逐项执行并报告结果）
1. ls 列出 ~/.zcode/ 下 AGENTS.md、rules（11 个 md）、skills（8 个目录）、
   agents（2 个 md）、hooks（2 个 js）确认数量与文件名一致。
2. 用 node -e "JSON.parse(...)" 校验 ~/.zcode/cli/config.json 可解析，
   且包含 hooks.events.PreToolUse / PostToolUse、mcp.servers（4 个）、
   plugins.enabledPlugins。
3. 打印 cli/config.json 中 hooks 的两条 command，确认路径已改为我的用户名。
4. 提示我重启 ZCode，并告知重启后如何逐项人工验证（MCP 工具出现、
   /技能命令可用、编辑 application-test.yml 被阻断等）。
```

> [!NOTE]
> 模板中的规则 A–F 与验证清单来自作者的实际踩坑经验：**JSON 整文件覆盖**会丢掉 ZCode 自身的运行时字段；**忘记改 hooks 路径**会让两个钩子静默失效；**tc-experts 插件**没有公开 marketplace 源。AI 按模板执行即可避开全部三个坑。

---

## 🧭 手动迁移详解（分步）

### Step 0 · 备份现有配置

> [!CAUTION]
> Step 7 会修改 `~/.zcode/cli/config.json`。**没有备份就不要动它**——该文件同时承载 ZCode 自身的运行时配置。

```bash
mkdir -p ~/.zcode/backup-$(date +%Y%m%d)
cp ~/.zcode/cli/config.json ~/.zcode/backup-$(date +%Y%m%d)/config.json.bak 2>/dev/null
cp -r ~/.zcode/rules    ~/.zcode/backup-$(date +%Y%m%d)/rules    2>/dev/null
cp -r ~/.zcode/skills   ~/.zcode/backup-$(date +%Y%m%d)/skills   2>/dev/null
cp ~/.zcode/AGENTS.md   ~/.zcode/backup-$(date +%Y%m%d)/AGENTS.md 2>/dev/null
echo "备份完成 → ~/.zcode/backup-$(date +%Y%m%d)/"
```

### Step 1 · 克隆本仓库

```bash
git clone <本仓库地址> zcode-si
cd zcode-si
```

### Step 2 · 安装 AGENTS.md（全局最高优先级准则）

`AGENTS.md` 是整套配置的**大脑**：定义了语言与称呼（回复以「主人」开头、全程中文）、决策优先级、编辑前强制检查清单、Git 只读白名单、L1/L2/L3 风险分级等全局硬规则。ZCode 每次会话自动读取它。

```bash
cp AGENTS.md ~/.zcode/AGENTS.md
```

- ✅ 落点：`~/.zcode/AGENTS.md`
- 🔍 验证：新开 ZCode 会话，回复应以「主人」开头且为中文
- 📄 该文件内所有 `~/.zcode/rules/...` 的引用都指向 Step 3 的落点，二者必须**成对安装**

### Step 3 · 安装 rules（11 个专项规则）

> [!IMPORTANT]
> **ZCode 不会自动加载 `rules/*.md`**——这是有意设计（区别于 Codex 的自动加载）。`AGENTS.md` 会在命中对应场景时（写业务代码、交付、多端对齐等）**主动读取**对应规则文件。所以 rules 和 AGENTS.md 必须同时安装。

```bash
mkdir -p ~/.zcode/rules
cp rules/*.md ~/.zcode/rules/
ls ~/.zcode/rules/   # 应看到 11 个 .md 文件
```

各文件作用见 [📜 Rules 规则速查表](#-rules-规则速查表)。

### Step 4 · 安装 skills（8 个技能）

```bash
mkdir -p ~/.zcode/skills
cp -r skills/. ~/.zcode/skills/
ls ~/.zcode/skills/   # 应看到 8 个目录
```

- ✅ 落点：`~/.zcode/skills/<技能名>/SKILL.md`（每个技能至少含一个带 YAML frontmatter 的 `SKILL.md`，部分技能带 `references/`、`assets/`、`bin/` 等子目录，**整体复制即可**）
- 🔍 验证：重启 ZCode 后，技能列表出现 8 个技能；显式技能可通过 `/技能名` 调用
- 🎓 具体每个技能怎么触发、怎么说，见 [🧩 Skills 使用详解](#-skills-使用详解怎么触发怎么用)

> [!TIP]
> `teach-me` 技能自带独立安装器（`package.json` + `install.js`），如果你还想在**单个项目内**使用它，可以在该项目目录执行 `npx github:Orange0618/teach-me-skill`，它会把 SKILL.md 装进项目的 `.agents/skills/teach-me/`。用户级安装（上面这步）已经全局生效，项目级安装是可选补充。

### Step 5 · 安装 agents（2 个只读审计子代理）

```bash
mkdir -p ~/.zcode/agents
cp agents/*.md ~/.zcode/agents/
```

- ✅ 落点：`~/.zcode/agents/annotation-auditor.md`、`~/.zcode/agents/cross-end-auditor.md`
- 📌 每个文件是带 frontmatter 的 Markdown：`name`（子代理加载名，注意 `annotation-auditor.md` 的加载名是 `annotation_auditor`，下划线）、`description`（主代理据此决定何时派发）、`tools: [Read, Bash]`（**只读**权限，不能改代码）
- 🔍 验证：重启后 ZCode 的 Agent 工具的可用类型列表中出现 `annotation_auditor` 与 `cross_end_auditor`

### Step 6 · 安装 hooks（2 个钩子脚本）

```bash
mkdir -p ~/.zcode/hooks
cp hooks/*.js ~/.zcode/hooks/
```

- ✅ 落点：`~/.zcode/hooks/guard-config-edit.js`、`~/.zcode/hooks/vue-parse-check.js`
- ⚠️ 此时脚本文件已就位，但**还没有被注册**——注册信息写在 `cli/config.json` 的 `hooks` 段，见 Step 7
- 🔍 两个脚本行为见 [🪝 Hooks 详解](#-hooks-详解)

### Step 7 · 配置 cli/config.json（hooks 注册 + MCP + 插件）

> [!CAUTION]
> **这一步是整个迁移中最容易出错的地方，请逐字阅读。**
>
> `~/.zcode/cli/config.json` 除了本仓库这三段配置外，**还包含 ZCode 自身运行时写入的其他字段**。因此：
>
> 1. ❌ **禁止**用仓库的 `cli/config.json` 直接覆盖目标文件
> 2. ✅ 必须**只合并** `hooks`、`mcp`、`plugins` 三段进去
> 3. ✅ hooks 的 `command` 路径必须改写成**你的**用户目录

**手动合并操作**：

① 先看仓库版三段内容（`cli/config.json`，只有 hooks / mcp / plugins 三段）：

```json
{
  "hooks": {
    "enabled": true,
    "events": {
      "PreToolUse":  [{ "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command", "command": "node \"C:/Users/caixi/.zcode/hooks/guard-config-edit.js\"" }] }],
      "PostToolUse": [{ "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command", "command": "node \"C:/Users/caixi/.zcode/hooks/vue-parse-check.js\"" }] }]
    }
  },
  "mcp": { "servers": { "chrome-devtools": { ... }, "context7": { ... },
                        "sequentialthinking": { ... }, "rea": { ... } } },
  "plugins": { "enabledPlugins": { "computer-use@zcode-plugins-official": true,
                                   "github@zcode-plugins-official": true,
                                   "claude-md-management@claude-plugins-official": true,
                                   "tc-experts@dev-tc-experts": true } }
}
```

② 打开你的 `~/.zcode/cli/config.json`，把上面三段**逐字段合入**（目标文件里已有的其他键保持不动）。

③ **改路径**：把两处 `C:/Users/caixi/` 替换为你的 Windows 用户主目录，例如：

```json
"command": "node \"C:/Users/<你的用户名>/.zcode/hooks/guard-config-edit.js\""
```

④ **处理插件**：`tc-experts@dev-tc-experts` 是作者私有 marketplace 的插件，你没有对应源 → 改为 `false` 或删除该行。官方三个插件保留 `true`，ZCode 会通过 `/plugin` 机制自动拉取官方 marketplace。

⑤ **不想手改 JSON？** 用下面这段幂等合并脚本（Python ≥ 3.11）一步完成：

```python
#!/usr/bin/env python3
"""把 zcode-si 的 hooks/mcp/plugins 三段合并进 ~/.zcode/cli/config.json（幂等）。"""
import json, shutil, sys
from pathlib import Path

REPO = Path("<填本仓库路径>")          # 例如 Path(r"F:\zcode-si")
USER = Path.home().name               # 自动取你的用户名，替换 caixi
target = Path.home() / ".zcode" / "cli" / "config.json"
src = json.loads((REPO / "cli" / "config.json").read_text(encoding="utf-8"))

target.parent.mkdir(parents=True, exist_ok=True)
cfg = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
if target.exists():
    shutil.copy2(target, target.with_suffix(".json.migrate-bak"))

cfg["hooks"] = src["hooks"]
cfg.setdefault("mcp", {})["servers"] = src["mcp"]["servers"]
cfg.setdefault("plugins", {})["enabledPlugins"] = src["plugins"]["enabledPlugins"]
cfg["plugins"]["enabledPlugins"]["tc-experts@dev-tc-experts"] = False   # 私有源，禁用

text = json.dumps(cfg, ensure_ascii=False, indent=2).replace(
    f"C:/Users/caixi/", f"C:/Users/{USER}/")
target.write_text(text, encoding="utf-8")
json.loads(target.read_text(encoding="utf-8"))   # 解析校验
print(f"OK → {target}（已备份 .migrate-bak）")
```

> [!WARNING]
> hooks 的 `command` 使用**正斜杠**绝对路径（`C:/Users/xxx/...`）且由 `node` 显式调用——这是作者在 Windows 下验证过的可靠写法，合并时不要改成反斜杠或相对路径。

### Step 8 · 重启并验证

完全退出 ZCode（含托盘图标）后重新启动，逐项检查：

- [ ] **AGENTS.md 生效**：新会话回复以「主人」开头、全中文
- [ ] **rules 就位**：`ls ~/.zcode/rules/` 显示 11 个 `.md`
- [ ] **skills 加载**：技能列表出现 8 个技能；输入 `/init`、`/deep-brainstorming` 等显式命令有响应
- [ ] **agents 加载**：Agent 工具类型中出现 `annotation_auditor`、`cross_end_auditor`
- [ ] **MCP 加载**：会话中出现 `mcp__chrome-devtools__*`、`mcp__context7__*`、`mcp__sequentialthinking__*`、`mcp__rea__*` 前缀的工具（首次启动 `npx` 要下载包，可能等待 1~3 分钟）
- [ ] **guard hook 生效**：让 AI 编辑一个 `application-test.yml` → 应被拦截并提示确认
- [ ] **vue-parse-check hook 生效**：编辑一个含语法错误的 `.vue` 文件 → 编辑后立即报语法错误（需要项目里有 `node_modules`）
- [ ] **插件**：官方插件在 `/plugin` 面板可见且已启用

任何一项失败 → 去看 [❓ FAQ 故障排查](#-faq-故障排查)。

---

## 🧩 Skills 使用详解（怎么触发、怎么用）

> [!NOTE]
> **Skills 的通用机制**：每个技能 = 一个目录 + `SKILL.md`（YAML frontmatter 里的 `description` 决定 AI 何时自动触发）。分两类：
> - **自动触发型**：AI 根据 description 判断当前任务命中就主动使用，你无需任何命令
> - **显式调用型**：需要你输入 `/技能名` 或说出触发语
>
> 想看某个技能的完整规则，直接打开 `~/.zcode/skills/<技能名>/SKILL.md` 阅读。

### 📊 archify — 架构图 / 流程图生成器（自动 + 可指定）

**用途**：把需求或已有 Mermaid 转成**可交互的独立 HTML 图表**：内联 SVG、深浅色主题、语义导航、节点聚焦、可选轨迹动画、1200×630 分享卡片 PNG，可导出 PNG/JPEG/WebP/SVG/WebM。支持架构图、工作流、时序图、数据流、状态机、CI/CD 流程等。

**触发示例**：
- 「帮我画一个订单系统的架构图」
- 「把这段 Mermaid 流程图美化为可交互的 HTML」
- 「画出这个接口调用的时序图，要能看每一步」

**产出**：一个双击即可在浏览器打开的 `*.html`（零依赖）。

### 🧠 deep-brainstorming — 深度头脑风暴（显式触发）

**用途**：针对**高影响、多因素、不确定性大**的决策做结构化深度推演（方案对比、盲区排查、风险矩阵）。

**触发方式**：输入 `/deep-brainstorming`，或明确说「对 XX 决策做一次深度头脑风暴」。
⚠️ 普通小问题不要用它，会得到大炮打蚊子式的长篇输出。

### 🏗️ init-project — 项目初始化（显式触发）

**用途**：扫描当前仓库，生成或刷新**项目级** `AGENTS.md`（或项目既有的等价 agent 指令文件），沉淀技术栈、目录结构、入口文件、构建命令等高频事实。

**触发方式**：输入 `/init`，或说「帮我初始化这个项目的 agent 指令文件」。
💡 与用户级 `~/.zcode/AGENTS.md` 是互补关系：用户级管「怎么协作」，项目级管「这个项目的事实」。

### 🔀 multi-end-align — 多端一致性对齐（自动 + 可指定）

**用途**：把 A 端（如 PC Web）的功能对齐到 B 端（移动 H5 / 微信端 / 小程序 / 微前端），执行 **12 步核验清单**与低代码页面分歧排查，逐字段比对接口 URL、入参、状态值、校验规则。

**触发示例**：
- 「把 PC 端的订单列表功能对齐到移动 H5，按多端对齐流程走」
- 「我们改了共享接口的字段，帮我核验两端的一致性」

### 📝 rules-doc-reviewer — 规则文档审查（自动 + 可指定）

**用途**：审查并规范化 `AGENTS.md` 与 `rules/*.md`：修复歧义表述、补全「触发条件 / 动作 / 判断标准」、合并重复规则、消除跨文件冲突。

**触发示例**：「帮我审查一下这套规则文档有没有表述歧义」「优化 AGENTS.md 的可执行性」。

### 💬 shuorenhua — 去 AI 味 / 审稿（显式触发为主）

**用途**：按你的要求**审稿或去除 AI 腔调**，支持中英文；保留事实、术语与责任主体，可只标问题不改文。

**触发示例**：「这段总结去一下 AI 味」「只标出问题，别改原文」「把这份周稿说人话」。

### 🎓 teach-me — AI 边教边做（自动触发）

**用途**：把 AI 从「代码生成器」变成「边教边做的导师」：拆解任务 → 讲解知识点 → **等你确认** → 边写边讲 → 回顾总结。适合项目驱动学习。

**触发示例**：
- 「请带我入门 SQLite，边做项目边教我」
- 「教我怎么实现这个登录模块，别直接甩代码」
- 「讲讲这段代码」（配合当前编辑器上下文）

### 🎨 ui-design — UI 设计 / 布局方案（自动 + 可指定）

**用途**：重新设计或改版界面、**对比多个布局方案**、产出设计原型 / 线框图。

**触发示例**：
- 「这个页面重新设计一下，给我 3 个布局方案对比」
- 「出一份设置页的线框图」

---

## 🪝 Hooks 详解

> [!IMPORTANT]
> Hooks 是**机制级强制**：不依赖 AI 自觉遵守规则，而是在工具调用层面直接拦截/检查。注册信息在 `~/.zcode/cli/config.json` 的 `hooks` 段，脚本本体在 `~/.zcode/hooks/`，二者缺一不可。

| 钩子 | 事件 | 触发条件（matcher） | 行为 |
|------|------|---------------------|------|
| `guard-config-edit.js` | `PreToolUse` | `Edit\|Write\|MultiEdit` 且目标文件名为 `application*.yml` / `application*.yaml` | **拒绝本次编辑**：向 stdout 输出 `permissionDecision: deny` 的 JSON 并附替代说明（退出码恒为 0）；未命中静默放行 |
| `vue-parse-check.js` | `PostToolUse` | `Edit\|Write\|MultiEdit` 后涉及 `.vue` / `.js` / `.mjs` | 对刚编辑的文件做**语法级解析**（从文件向上找最近 `node_modules` 取解析器）；发现语法错误以 exit 2 + stderr 报错促使当场修复；解析器不可用时静默放行，绝不阻塞正常编辑 |

**工作原理**：ZCode 在每次 Edit/Write 工具调用前后，把工具输入（JSON，含 `file_path` / `tool_input`）通过 **stdin** 传给脚本。两个脚本的拦截/反馈协议不同：
- `guard-config-edit.js`（PreToolUse）→ stdout 输出 `hookSpecificOutput: { permissionDecision: "deny", permissionDecisionReason: "..." }`，由 ZCode 拒绝该次工具调用
- `vue-parse-check.js`（PostToolUse）→ exit `2` + stderr，把语法错误回传给 AI 促使其立即修复；exit `0` 表示通过或放行

**修改 / 扩展钩子**：直接编辑 `~/.zcode/hooks/*.js` 后重启 ZCode 生效；新增钩子需同时在 `cli/config.json` 的 `hooks.events` 里注册（结构照抄现有两条即可）。

---

## 🔌 MCP 服务器详解

> [!NOTE]
> MCP（Model Context Protocol）给 AI 提供外部工具能力。本配置经 `npx` 启动 4 个 stdio 服务器，**首次启动需联网下载 npm 包**（1~3 分钟），之后走本地缓存。全部无需 API Key。

| 服务器 | npm 包 | 用途 | 何时被使用 |
|--------|--------|------|-----------|
| `chrome-devtools` | `chrome-devtools-mcp@latest`（`--autoConnect`） | 浏览器自动化：打开页面、截图、DOM 快照、点击/填表、网络请求、性能追踪 | 前端调试、页面验证、E2E 走查 |
| `context7` | `@upstash/context7-mcp` | 查询任意编程库的**最新官方文档与代码示例** | 使用不熟悉的库 / 新版本 API 时 |
| `sequentialthinking` | `@modelcontextprotocol/server-sequential-thinking` | 结构化分步推理（可分支、可回溯的思考链） | 复杂问题拆解、方案推演 |
| `rea` | `rea-agents@6.4.0` | 高级分析套件：二进制 / 逆向分析、进程与 Web 捕获对比、证据链管理 | 逆向工程、深度安全分析等特殊场景 |

**验证方法**：重启 ZCode 后，工具列表中出现 `mcp__chrome-devtools__*`、`mcp__context7__*` 等前缀的工具即成功。
**增加服务器**：在 `cli/config.json` 的 `mcp.servers` 下按同构添加（`stdio` 型给 `command` + `args`，HTTP 型用 `{"type":"http","url":"..."}`）。

---

## 👥 自定义 Agents 详解

两个自定义子代理都是**只读审计员**（`tools: [Read, Bash]`，无法改代码），由主代理在交付前**派发交叉审查**，结论不替代主代理判断：

| 加载名 | 文件 | 职责 | 典型派发场景 |
|--------|------|------|--------------|
| `annotation_auditor` | `agents/annotation-auditor.md` | 业务注释一致性审查：方法体业务段落注释、数据库调用注释六要素、跨边界字段契约、Javadoc 标签合法性 | 涉及业务逻辑 / MyBatis SQL / 公共 API 的修改**交付前** |
| `cross_end_auditor` | `agents/cross-end-auditor.md` | 多端业务一致性审计：逐字段比对两端接口 URL、入参、状态值、校验、禁用态、数据源 | 多端对齐、同步改造、共享接口 / 字典 / 状态机变更 |

审查标准引用 `~/.zcode/rules/annotation.md` 与多端对齐流程——所以 **agents 依赖 rules 一起安装**。

---

## 📜 Rules 规则速查表

> [!IMPORTANT]
> 再次强调：ZCode **不会**自动加载 `rules/*.md`。`AGENTS.md` 会在对应场景被命中时引用读取它们，因此 rules 是 AGENTS.md 的**配套必需品**。

| 文件 | 一句话职责 | 主要被引用场景 |
|------|-----------|----------------|
| `annotation.md` | 业务注释强制标准（六要素、A/B/C/R 档、编辑前清单） | 任何业务代码 Edit/Write 之前 |
| `business-assumptions.md` | 业务假设显式化与数据验证 | 无法确认业务意图、涉及数据口径时 |
| `delivery.md` | 交付结构模板（标准 / 简化）、风险分级 | 代码变更交付时 |
| `design-principles.md` | 设计模式与组件化的选用与决策矩阵 | 新增能力、历史代码修复 |
| `engineering-core.md` | 安全编码、持久层、性能、渐进式架构治理、第三方依赖字节码核实 | 通用工程任务 |
| `frontend.md` | 前端工程规范、组件抽取标准、禁 build/lint 的等效静态验证 | 前端修改 |
| `pitfalls.md` | 后端 / 前端 / 历史项目高频陷阱速查 | 排查与编码过程 |
| `response-quality.md` | 回复质量：事实证据、编号、行动导向、发送前自检 | 组织面向用户的回复 |
| `subagent.md` | 子代理派发与输出约束 | 派发 Subagent 时 |
| `version-control.md` | Git 只读白名单、敏感配置处理 | 版本控制相关操作 |
| `workflows.md` | 工作流路由、多端一致性对齐、修改后影响面审查 | 开发任务入口 |

---

## ❓ FAQ 故障排查

<details>
<summary><b>🔁 MCP 服务器一直没出现 / 启动失败</b></summary>

1. `node -v` 与 `npx -v` 是否可用（Node 建议当前 LTS）
2. 首次启动 `npx` 要下载包，耐心等 1~3 分钟；检查网络 / npm 镜像
3. 手动验证单个服务器能否启动：`npx -y @upstash/context7-mcp`（应挂起等待 stdin，Ctrl+C 退出即正常）
4. 确认合并后 `cli/config.json` 是合法 JSON（`node -e "JSON.parse(require('fs').readFileSync(process.env.USERPROFILE+'/.zcode/cli/config.json'))"`)
</details>

<details>
<summary><b>🪝 编辑 application.yml 没有被拦截</b></summary>

1. 打开 `cli/config.json`，确认 `hooks.enabled` 为 `true`，`PreToolUse` 存在且 matcher 为 `Edit|Write|MultiEdit`
2. 确认 `command` 里的路径是**你的**用户目录（最常见的失效原因就是没改 `caixi`）
3. 手动测试脚本：`echo '{"tool_input":{"file_path":"C:/x/application-prod.yml"}}' | node ~/.zcode/hooks/guard-config-edit.js`，stdout 应输出含 `permissionDecision: "deny"` 的 JSON
4. 重启 ZCode（hooks 注册只在启动时读取）
</details>

<details>
<summary><b>🧩 技能列表里看不到某个技能</b></summary>

1. 确认目录结构：`~/.zcode/skills/<技能名>/SKILL.md` 必须存在，且 frontmatter 有 `name` 与 `description`
2. `deep-brainstorming` 设计上**仅显式触发**（`/deep-brainstorming`），不自动出现很正常
3. Windows 下注意复制时是否产生了嵌套目录（如 `skills/skills/archify`）
</details>

<details>
<summary><b>👥 Agent 工具里没有 annotation_auditor / cross_end_auditor</b></summary>

1. 确认 `~/.zcode/agents/` 下两个 `.md` 存在，frontmatter 的 `name` 值分别是 `annotation_auditor`、`cross_end_auditor`
2. 这些子代理的审查标准引用 `~/.zcode/rules/annotation.md` 等，rules 缺失会导致派发后行为不完整
</details>

<details>
<summary><b>🖥️ AI 回复不是中文 / 没有「主人」称呼</b></summary>

`~/.zcode/AGENTS.md` 未生效：确认文件在 `~/.zcode/AGENTS.md`（不是项目目录下），且没有在其他更高优先级的项目级指令里被覆盖。
</details>

<details>
<summary><b>🧨 vue-parse-check 一直静默没反应</b></summary>

该脚本设计为「解析器不可用即静默放行」：它需要被编辑文件向上能找到 `node_modules`。纯后端 / 无 Node 项目不触发是**预期行为**。
</details>

<details>
<summary><b>📦 tc-experts 插件报错</b></summary>

`tc-experts@dev-tc-experts` 来自作者私有 marketplace，公开渠道没有。把 `cli/config.json` 中该项改为 `false` 即可。
</details>

---

## 🔐 安全与隐私

- 🚫 `AGENTS.md` 与 `rules/version-control.md` 强制 **Git 只读白名单**：AI 不允许执行任何 Git 写操作（commit / push / branch 变更），变更一律留在工作区由你决定提交与否——这是有意为之的安全设计
- 🛡️ `guard-config-edit.js` 会拦截 `application*.yml` 编辑，防止 AI 擅自改动含数据源密码的配置
- 🧹 本仓库**不包含**任何 API Key / token；模型服务的登录凭据由 ZCode 自身的账号体系管理，不随配置迁移

---

## ✅ 迁移完成检查清单

- [ ] 前置条件满足：ZCode、Node.js（LTS）、Git 就绪
- [ ] 已备份 `~/.zcode/cli/config.json` 与原有 rules/skills
- [ ] `~/.zcode/AGENTS.md` 已安装
- [ ] `~/.zcode/rules/` 共 **11** 个 `.md`
- [ ] `~/.zcode/skills/` 共 **8** 个技能目录
- [ ] `~/.zcode/agents/` 共 **2** 个 `.md`
- [ ] `~/.zcode/hooks/` 共 **2** 个 `.js`
- [ ] `cli/config.json` 已**合并**（非覆盖）hooks / mcp / plugins 三段，JSON 可解析
- [ ] hooks `command` 路径已改为**你的用户目录**
- [ ] `tc-experts@dev-tc-experts` 已置 `false`
- [ ] 重启 ZCode 后 Step 8 的 8 项验证全部通过

全部打勾后，这套配置在新机器上与作者环境完全等价 🎉

---

<div align="center">

**🧩 zcode-si** · 让每一次 AI 协作都有章法 · Config as Code

</div>
