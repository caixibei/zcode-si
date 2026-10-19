#!/usr/bin/env node
/**
 * PostToolUse hook（用户级通用）：前端源码编辑后的纯语法解析校验（等效静态验证，非 lint、非构建）。
 *
 * 业务背景：全局 frontend.md 禁止对前端项目执行 build/lint，但允许 Vue 模板/脚本
 * 解析等"等效静态验证"。本脚本在每次 Edit/Write 之后，对触及的前端源文件做语法级
 * 解析，把"改完才发现模板/脚本写错"前移为"编辑后立即反馈、当场修复"。
 *
 * 行为契约：
 * 1. 校验任意项目的 .vue / .js / .mjs 源文件（解析器可用时），不干扰后端与配置编辑。
 * 2. 解析器不可用或脚本自身异常时一律静默放行（exit 0），绝不阻塞正常编辑流程。
 * 3. 发现语法错误时以 exit 2 + stderr 返回，Codex 收到后应立即读取文件修复后再继续。
 */
const fs = require('fs');
const path = require('path');

// 从被编辑文件向上查找最近的 node_modules；找不到说明不是 Node/Vue 项目，直接放行
function findProjectDir(startFile) {
  let dir = path.dirname(path.resolve(startFile));
  for (;;) {
    if (fs.existsSync(path.join(dir, 'node_modules'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

// stdin 读取：hook 入参为一次 JSON；解析失败视为无有效输入，直接放行
let raw = '';
try { raw = fs.readFileSync(0, 'utf8'); } catch (e) { process.exit(0); }
let payload = null;
try { payload = JSON.parse(raw); } catch (e) { process.exit(0); }

// Codex apply_patch 使用 tool_input.command；其他编辑类输入可能直接提供 file_path。
const toolInput = (payload && payload.tool_input) || {};
let targets = [];
if (toolInput.file_path) targets.push(toolInput.file_path);
if (typeof toolInput.command === 'string') {
  for (const line of toolInput.command.split(/\r?\n/)) {
    const match = line.match(/^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$/);
    if (match) targets.push(match[1]);
  }
}

targets = targets
  .map((filePath) => filePath.replace(/\\/g, '/'))
  .filter((normPath) => /\.(vue|js|mjs)$/.test(normPath))
  .filter((normPath) => !/node_modules|\/dist\/|\.min\.js$/.test(normPath));
if (!targets.length) process.exit(0);

// 项目根定位：非 Node/Vue 项目（无 node_modules）不校验，直接放行
const projectDir = findProjectDir(targets[0]);
if (!projectDir) process.exit(0);

const errors = []; // 元素形如 { label, line, column, message }，最终聚合成 stderr 反馈

// 解析器加载：从被编辑文件所在项目的 node_modules 解析；缺失时返回 null，由调用方降级跳过
function loadParser(names) {
  for (const name of names) {
    try {
      return require(require.resolve(name, {
        paths: [projectDir],
      }));
    } catch (e) {
      // 解析器缺失属正常降级场景，继续尝试下一个候选
    }
  }
  return null;
}

// Vue 主版本判定：读项目 vue 包版本 major 位，2 → vue-template-compiler，3 → @vue/compiler-sfc；
// 项目未装 vue（纯 JS 项目）或读取失败时返回 null，.vue 文件按 Vue2 路径尝试后降级
function detectVueMajor() {
  try {
    const pkg = require(require.resolve('vue/package.json', { paths: [projectDir] }));
    return parseInt(pkg.version, 10);
  } catch (e) {
    return null;
  }
}

// 脚本语法解析：@babel/parser 支持现代语法与 JSX/TS；解析器缺失时跳过，不留误报
function checkScript(code, label, lang) {
  if (!code || !code.trim()) return;
  const babelParser = loadParser(['@babel/parser']);
  if (!babelParser) return;
  const plugins = ['jsx'];
  if (lang === 'ts') plugins.push('typescript');
  try {
    // sourceType unambiguous：按是否出现 import/export 自动判定模块模式，
    // 兼容 ESM 页面代码与含 require 的历史脚本；纯语法解析，不做变量与引用检查
    babelParser.parse(code, {
      sourceType: 'unambiguous',
      allowReturnOutsideFunction: true,
      plugins,
    });
  } catch (e) {
    errors.push({
      label,
      line: e.loc && e.loc.line,
      column: e.loc && e.loc.column,
      message: e.message,
    });
  }
}

// Vue 2 SFC 解析：vue-template-compiler 只校验模板语法；script 段交给 babel 检查
function checkVue2Sfc(source) {
  const compiler = loadParser(['vue-template-compiler']);
  if (!compiler) return;
  const sfc = compiler.parseComponent(source);
  if (sfc.template && sfc.template.content) {
    const result = compiler.compile(sfc.template.content);
    for (const err of result.errors || []) {
      errors.push({ label: 'template', message: typeof err === 'string' ? err : err.msg });
    }
  }
  if (sfc.script) checkScript(sfc.script.content, 'script', sfc.script.lang);
}

// Vue 3 SFC 解析：@vue/compiler-sfc 来自当前项目自身依赖；未安装时降级为
// 仅提取 <script> 文本做纯 JS 语法检查，不使用 Vue 2 编译器解析 Vue 3 模板（避免误报）
function checkVue3Sfc(source, filePath) {
  let sfcParser = null;
  try {
    sfcParser = require(require.resolve('@vue/compiler-sfc', {
      paths: [projectDir],
    }));
  } catch (e) {
    // Vue3 编译器缺失：跳过模板检查，script 检查走下方降级分支
  }
  if (sfcParser) {
    const { descriptor, errors: parseErrors } = sfcParser.parse(source, { filename: filePath });
    for (const err of parseErrors || []) {
      errors.push({ label: 'sfc', message: err.message || String(err) });
    }
    if (descriptor && descriptor.template && descriptor.template.content) {
      const tpl = sfcParser.compileTemplate({
        source: descriptor.template.content,
        filename: filePath,
        id: 'hook-check',
      });
      for (const err of tpl.errors || []) {
        errors.push({ label: 'template', message: err.message || String(err) });
      }
    }
    if (descriptor && descriptor.script) {
      checkScript(descriptor.script.content, 'script', descriptor.script.lang);
    }
    if (descriptor && descriptor.scriptSetup) {
      checkScript(descriptor.scriptSetup.content, 'script setup', descriptor.scriptSetup.lang);
    }
  } else if (/<script[^>]*>/.test(source)) {
    const match = source.match(/<script([^>]*)>([\s\S]*?)<\/script>/);
    if (match) {
      const langMatch = match[1].match(/lang="([^"]+)"/);
      checkScript(match[2], 'script', langMatch && langMatch[1]);
    }
  }
}

// 主分派：按扩展名与项目 vue 主版本选择解析器；解析流程自身异常不得影响编辑主流程
for (const filePath of targets) {
  let source = '';
  try { source = fs.readFileSync(filePath, 'utf8'); } catch (e) { continue; }
  const errorStart = errors.length;
  try {
    if (filePath.endsWith('.vue')) {
      const vueMajor = detectVueMajor();
      if (vueMajor === 3) checkVue3Sfc(source, filePath);
      else checkVue2Sfc(source);
    } else {
      checkScript(source, 'script');
    }
  } catch (e) {
    continue;
  }
  for (let i = errorStart; i < errors.length; i++) errors[i].file = filePath;
}

// 结果反馈：存在语法错误时 exit 2，stderr 会回传给 Codex，触发当场读取修复
if (errors.length > 0) {
  const lines = errors.map((e) => {
    const where = e.line ? ` 第 ${e.line} 行${e.column ? ` 第 ${e.column} 列` : ''}` : '';
    return `  [${path.basename(e.file || '')}${e.label ? ` ${e.label}` : ''}${where}] ${e.message}`;
  });
  process.stderr.write(`前端源码语法解析未通过：\n${lines.join('\n')}\n`);
  process.exit(2);
}
process.exit(0);
