#!/usr/bin/env node

/*
 * teach-me-skill — install script
 *
 * Copies the Teach Me skill into the current project so any
 * skill-capable coding agent (Claude Code, ZCode, etc.) can load
 * it automatically.
 *
 * Usage:  npx teach-me-skill
 *         npx teach-me-skill /path/to/project
 *
 * The script creates the skill directory for each well-known agent
 * location at once (`.claude/skills/`, `.agents/skills/`), so the
 * project works with whichever tool opens it next. Duplicate copies
 * are harmless — pick ONE primary location and symlink the rest if
 * you want them to stay in sync.
 */

const fs   = require('fs');
const path = require('path');

// --- helpers -------------------------------------------------------

function mkdirp(dir) {
    fs.mkdirSync(dir, { recursive: true });
}

function copyFile(src, dst) {
    fs.copyFileSync(src, dst);
}

// Well-known per-project skill directories across coding agents.
const SKILL_DIRS = [
    '.claude/skills',  // Claude Code
    '.agents/skills',  // ZCode and the cross-tool standard location
];

// --- main ----------------------------------------------------------

function main() {
    // The user can optionally pass a project root as an argument.
    const targetRoot = process.argv[2]
        ? path.resolve(process.argv[2])
        : process.cwd();

    // Where the skill lives inside THIS package (shipped alongside install.js).
    const pkgRoot  = path.resolve(__dirname);
    const srcFile  = path.join(pkgRoot, 'SKILL.md');

    console.log('\n  📦 teach-me-skill  v1.1.0\n');
    console.log('  Installing Teach Me skill...');
    console.log(`    project : ${targetRoot}\n`);

    for (const skillDir of SKILL_DIRS) {
        const dir     = path.join(targetRoot, skillDir, 'teach-me');
        const dstFile = path.join(dir, 'SKILL.md');
        mkdirp(dir);
        copyFile(srcFile, dstFile);
        console.log(`    ✓ ${path.relative(targetRoot, dstFile)}`);
    }

    console.log('\n  ✅ Teach Me skill installed!\n');
    console.log('  Try it now:');
    console.log('    /teach-me 教我完成...\n');
}

main();
