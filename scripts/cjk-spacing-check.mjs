#!/usr/bin/env node
// CJK ↔ half-width spacing checker
// Checks staged/given files (Markdown / MDX / HTML / Astro) or rendered output (dist/**/*.html)
//
// Rules (Drupal conventions):
//   1. CJK ↔ English letter → need space
//   2. CJK ↔ digit → need space
//   3. Digit <-> Date units (Year/Month/Day) -> need space
//   4. Half-width parens adjacent to CJK → need space outside
//   5. Number followed by ' %' → strip space (100% not 100 %)
//
// Usage:
//   node scripts/cjk-spacing-check.mjs [--staged] [--build] [FILE ...]

import { execSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const DIST = join(ROOT, 'dist')

// ── args ───────────────────────────────────────────────────────────────────
const args = process.argv.slice(2)
const isStaged = args.includes('--staged')
const doBuild = args.includes('--build')
let files = args.filter((a) => !a.startsWith('--'))

if (doBuild) {
  console.log('Building...')
  execSync('npm run build', { cwd: ROOT, stdio: 'inherit' })
}

if (isStaged) {
  try {
    const stagedOutput = execSync('git diff --cached --name-only --diff-filter=ACM', {
      cwd: ROOT,
      encoding: 'utf-8',
    })
    const stagedFiles = stagedOutput
      .split('\n')
      .map((f) => f.trim())
      .filter((f) => f && /\.(md|mdx|html|astro|txt)$/i.test(f))
    files = stagedFiles.map((f) => join(ROOT, f))
  } catch {
    files = []
  }
  if (files.length === 0) {
    process.exit(0)
  }
}

// ── collect HTML files if no explicit files given ───────────────────────────
function collectHtml(dir) {
  if (!existsSync(dir)) return []
  const results = []
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) {
      results.push(...collectHtml(full))
    } else if (entry.endsWith('.html')) {
      results.push(full)
    }
  }
  return results
}

const targetFiles = files.length > 0 ? files : collectHtml(DIST)

if (targetFiles.length === 0) {
  console.log('No files to check.')
  process.exit(0)
}

// ── clean content to plain text ────────────────────────────────────────────
function cleanContent(content, isHtml) {
  if (isHtml) {
    return content
      .replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<!--[\s\S]*?-->/g, '')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<hr\s*\/?>/gi, '\n')
      .replace(
        /<\/(div|p|li|tr|h[1-6]|section|article|header|footer|nav|main|aside|dl|dd|dt|head|body|title|button|svg|g|text)>/gi,
        '\n'
      )
      .replace(/<\/(span|a|strong|em|code|b|i|small|sub|sup|mark|label|option)>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&nbsp;/g, ' ')
      .replace(/[^\S\n]+/g, ' ')
      .replace(/\n\s*\n/g, '\n')
      .trim()
  }

  // Markdown / MDX / source file handling
  return content
    .split('\n')
    .map((line) => {
      // strip code blocks / inline code / html tags / URLs
      return line
        .replace(/`[^`]*`/g, '')
        .replace(/<[^>]*>/g, '')
        .replace(/https?:\/\/[^\s)\]]+/g, '')
        .replace(/——/g, '')
    })
    .join('\n')
}

// ── check rules ────────────────────────────────────────────────────────────
const CJK = '[\\u4e00-\\u9fff\\u3400-\\u4dbf\\uf900-\\ufaff]'

const rules = [
  {
    name: 'CJK↔EN',
    desc: 'Missing space between CJK and English letter',
    pattern: new RegExp(`(${CJK})([A-Za-z])|([A-Za-z])(${CJK})`, 'g'),
  },
  {
    name: 'CJK↔DIG',
    desc: 'Missing space between CJK and number',
    pattern: new RegExp(`(${CJK})([0-9])|([0-9])(${CJK})`, 'g'),
  },
  {
    name: 'DATE',
    desc: 'Missing space between number and 年/月/日',
    pattern: /([0-9])([年月日])|([年月日])([0-9])/g,
  },
  {
    name: 'PAREN',
    desc: 'Need space outside half-width parens next to CJK',
    pattern: new RegExp(`(${CJK})\\(|\\)(${CJK})`, 'g'),
  },
  {
    name: 'PERCENT',
    desc: "Space before '%' should be removed (use 100%)",
    pattern: /([0-9]) %/g,
  },
]

// ── run ────────────────────────────────────────────────────────────────────
let totalViolations = 0

for (const file of targetFiles) {
  if (!existsSync(file)) continue
  const rel = relative(ROOT, file)
  if (rel.includes('node_modules') || rel.includes('.git')) continue

  const raw = readFileSync(file, 'utf-8')
  const isHtml = file.endsWith('.html')
  const text = cleanContent(raw, isHtml)

  const lines = text.split('\n')
  const violations = []

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
    const line = lines[lineIndex]
    if (!new RegExp(CJK).test(line)) continue

    for (const rule of rules) {
      rule.pattern.lastIndex = 0
      let match = rule.pattern.exec(line)
      while (match !== null) {
        const start = Math.max(0, match.index - 15)
        const end = Math.min(line.length, match.index + match[0].length + 15)
        const context = line.slice(start, end).trim()
        violations.push({
          line: lineIndex + 1,
          rule: rule.name,
          match: match[0],
          context,
          desc: rule.desc,
        })
        match = rule.pattern.exec(line)
      }
    }
  }

  if (violations.length > 0) {
    console.log(`\n${rel}:`)
    for (const v of violations) {
      console.log(`  L${v.line} [${v.rule}] "${v.match}" — ${v.desc}`)
      console.log(`    …${v.context}…`)
    }
    totalViolations += violations.length
  }
}

if (totalViolations === 0) {
  console.log('CLEAN — no CJK spacing violations.')
  process.exit(0)
} else {
  console.log(`\n${totalViolations} violation(s) found.`)
  process.exit(1)
}
