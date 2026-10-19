#!/usr/bin/env node
/**
 * PreToolUse hook（用户级通用）：环境配置文件（application*.yml）编辑前阻断。
 *
 * 业务背景：各项目的 application*.yml 通常包含真实数据源等敏感配置，敏感配置
 * 修改前应由用户确认。本 hook 把该约定硬化为机制：命中目标文件名时拒绝本次
 * 编辑并返回替代说明；未命中时静默放行，不给普通编辑增加确认负担。
 */
const fs = require('fs');

let raw = '';
try { raw = fs.readFileSync(0, 'utf8'); } catch (e) { process.exit(0); }
let payload = null;
try { payload = JSON.parse(raw); } catch (e) { process.exit(0); }

// Codex apply_patch 使用 tool_input.command；其他编辑类输入可能直接提供 file_path。
const toolInput = (payload && payload.tool_input) || {};
const targets = [];
if (toolInput.file_path) targets.push(toolInput.file_path);
if (typeof toolInput.command === 'string') {
  for (const line of toolInput.command.split(/\r?\n/)) {
    const match = line.match(/^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$/);
    if (match) targets.push(match[1]);
  }
}

const fileNames = targets.map((filePath) => filePath.replace(/\\/g, '/').split('/').pop() || '');

if (fileNames.some((fileName) => /^application.*\.ya?ml$/i.test(fileName))) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: '该文件为环境配置文件，可能含数据源等敏感配置；Codex hooks 当前不支持 ask，请提供具体字段与改动的明确授权后由用户在会话外或通过安全替代方案处理。',
    },
  }));
}
process.exit(0);
