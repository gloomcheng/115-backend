#!/usr/bin/env node
// Render-integrity guard.
//
// Three defect classes that got through the other 16 checks, each found by
// reading the built pages or the built output rather than the source:
//
//   1. Markdown emphasis that CommonMark refuses to parse. A ** delimiter run
//      must be left-flanking to open and right-flanking to close, and a CJK
//      ideograph is neither whitespace nor punctuation. So a run sitting after
//      a CJK full stop and before a CJK character renders as literal
//      asterisks, and so does a run followed by a space. This silently
//      affected 337 paragraphs across the sixteen lessons before it was found.
//      The rule below is transcribed from a matrix produced by running the
//      site's own unified/remark over every combination of neighbouring
//      character class, not from reasoning about the spec.
//
//   2. A Callout nested inside another Callout. Callout renders with 28px
//      padding, a 4px left border and 32px vertical margin, so a nested one is
//      a coloured box floating in the outer box's background.
//
//   3. A section cross-reference whose claim is not in the section it points
//      at: a reference to one section while naming a term that only ever
//      appears in another. The reference resolves to a real section, so
//      existence checks pass; only the claim is wrong.
//
// Also catches unbalanced Callout tags, which silently swallow content.
//
// Usage: node scripts/render-integrity-harness.mjs [--staged]

import { execSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const isStaged = process.argv.includes('--staged')

// ── collect sources ───────────────────────────────────────────────────────
const explicit = (() => {
  const i = process.argv.indexOf('--files')
  return i === -1 ? null : process.argv.slice(i + 1).filter(Boolean)
})()

function collectFiles() {
  if (explicit) return explicit
  if (!isStaged) {
    const out = execSync("git ls-files 'src/content/lessons/*.mdx' 'src/content/docs/*.mdx'", {
      cwd: ROOT,
      encoding: 'utf8',
    })
    return out.split('\n').filter(Boolean)
  }
  try {
    const out = execSync('git diff --cached --name-only --diff-filter=ACM', {
      cwd: ROOT,
      encoding: 'utf8',
    })
    return out.split('\n').filter((f) => /\.(mdx|md)$/.test(f))
  } catch {
    return []
  }
}

// ── character classes ─────────────────────────────────────────────────────
const CJK_PUNCT = '。、，：；！？（）「」『』《》【】…—～'
const isWs = (ch) => ch === '' || /\s/.test(ch)
const isPunct = (ch) => {
  if (!ch) return false
  if (CJK_PUNCT.includes(ch)) return true
  return /[!-/:-@[-`{-~]/.test(ch) // ASCII punctuation, which includes `
}

// ── regions that are not prose ────────────────────────────────────────────
// Inside these, ** is literal content: shell comments, HTTP headers, SQL
// injection samples, .dockerignore listings. Fixing them would corrupt the
// material.
//
// Inline code is masked too, and that matters for both checks. One lesson
// mentions the Callout tag inside a code span; counting that as an opening tag
// desynchronised the nesting stack and produced two phantom nested Callouts
// later on.
function proseMask(line, state) {
  if (/^\s*```/.test(line)) {
    state.fence = !state.fence
    return null
  }
  if (state.fence) return null
  const t = line.trimStart()
  if (t.startsWith('<Terminal')) state.inTerminal = true
  if (state.inTerminal) {
    if (/`\}\s*<\/Terminal>\s*$/.test(t) || t.endsWith('</Terminal>')) {
      state.inTerminal = false
    }
    return null
  }
  // Markdown table rows are not prose.
  if (t.startsWith('|')) return null
  // Blank out inline code spans, keeping offsets and the delimiting backticks
  // stable. The backticks matter: they are ASCII punctuation, so keeping them
  // preserves how CommonMark sees the flanking of a neighbouring **.
  const TICK = '`'
  return line.replace(/`[^`\n]*`/g, (m) => `${TICK}${'x'.repeat(m.length - 2)}${TICK}`)
}

// ── check 1 & 3 ───────────────────────────────────────────────────────────
// Scoped to lines that contain at least two ** runs. A lone run is not
// evidence: bold may legitimately span lines inside a paragraph, so pairing is
// only judged within a line that closes what it opens.
function checkEmphasis(lines, path, findings) {
  const state = { fence: false, inTerminal: false }
  lines.forEach((raw, i) => {
    const line = proseMask(raw, state)
    if (line === null) return
    const positions = [...line.matchAll(/\*\*/g)].map((m) => m.index)
    if (positions.length < 2) return
    positions.forEach((idx, order) => {
      const prev = idx > 0 ? line[idx - 1] : ''
      const next = idx + 2 < line.length ? line[idx + 2] : ''
      const opener = order % 2 === 0
      if (opener) {
        // left-flanking fails when followed by whitespace, or followed by
        // punctuation while preceded by neither whitespace nor punctuation
        if (next === ' ') {
          findings.push({
            path,
            line: i + 1,
            rule: 'emphasis-unparsed/opening-then-space',
            match: line.slice(Math.max(0, idx - 24), idx + 18),
            fix: 'delete the space after the opening **',
          })
        } else if (isPunct(next) && !isWs(prev) && !isPunct(prev)) {
          findings.push({
            path,
            line: i + 1,
            rule: 'emphasis-unparsed/opening-then-punctuation',
            match: line.slice(Math.max(0, idx - 24), idx + 18),
            fix: 'put a space before the opening **',
          })
        }
      } else {
        // right-flanking fails when preceded by punctuation and followed by
        // neither whitespace nor punctuation
        if (isPunct(prev) && !isWs(next) && !isPunct(next)) {
          findings.push({
            path,
            line: i + 1,
            rule: 'emphasis-unparsed/closing-after-punctuation',
            match: line.slice(Math.max(0, idx - 24), idx + 18),
            fix: 'put a space after the closing **',
          })
        }
      }
    })
  })
}

// ── check 2: Callout nesting and balance ──────────────────────────────────
function checkCallouts(lines, path, findings) {
  const state = { fence: false, inTerminal: false }
  const stack = []
  lines.forEach((raw, i) => {
    const masked = proseMask(raw, state)
    if (masked === null) return
    for (const _ of masked.matchAll(/<Callout\b/g)) {
      const tag = raw.match(/<Callout\b[^>]*>/)?.[0] ?? ''
      const title = tag.match(/title="([^"]*)"/)?.[1] ?? '(no title)'
      stack.push({ line: i + 1, title })
      if (stack.length > 1) {
        findings.push({
          path,
          line: i + 1,
          rule: 'callout-nested',
          match: `「${stack[stack.length - 1].title}」 inside 「${stack[0].title}」`,
          fix: 'close the outer Callout before this one, or fold the content in',
        })
      }
    }
    for (const _ of masked.matchAll(/<\/Callout>/g)) {
      if (stack.length === 0) {
        findings.push({
          path,
          line: i + 1,
          rule: 'callout-unbalanced',
          match: '</Callout> with no opening tag',
          fix: 'remove the stray closing tag',
        })
      } else {
        stack.pop()
      }
    }
  })
  for (const open of stack) {
    findings.push({
      path,
      line: open.line,
      rule: 'callout-unbalanced',
      match: `never closed: 「${open.title}」`,
      fix: 'add the missing </Callout>',
    })
  }
}

// ── section index, for check 3 ───────────────────────────────────────────
// Stores the section body as well as its title. A reference that quotes a
// sentence from inside a section is not referring to its heading, so comparing
// a claim against the title alone reports every such case as broken.
function sectionIndex(text) {
  const map = new Map()
  const heads = [...text.matchAll(/^(#{2,3}) (\d+)\. (.+)$/gm)]
  heads.forEach((m, i) => {
    const num = Number(m[2])
    if (map.has(num)) return
    const start = m.index + m[0].length
    const end = i + 1 < heads.length ? heads[i + 1].index : text.length
    map.set(num, { title: m[3].trim(), body: text.slice(start, end) })
  })
  return map
}

// A claim is only checkable when it names something concrete: a `code` span
// or a 「quoted term」 right after the reference.
function checkCrossRefs(text, path, own, byUnit, findings) {
  const body = text.replace(/```[\s\S]*?```/g, '')
  for (const m of body.matchAll(/(?:單元 (\d+)[^。\n]{0,12}?)?第 (\d+) 節([^。\n]{0,20})/g)) {
    const cross = m[1]
    const num = Number(m[2])
    let tail = m[3] || ''
    // The window is deliberately short. A claim belongs to the reference it
    // sits next to, not to every quoted term later in the same sentence: a
    // section reference followed by an em-dash clause can carry a quoted term
    // that belongs to the sentence's own section, not the referenced one.
    const nextRef = tail.search(/(?:單元 \d+[^。\n]{0,12}?)?第 \d+ 節/)
    if (nextRef > 0) tail = tail.slice(0, nextRef)
    // A same-file reference resolves against this file's own sections. Using a
    // shared default here silently resolved unit 17 against the AI guide.
    const target = cross ? byUnit.get(Number(cross)) : own
    if (!target) continue
    const section = target.get(num)
    if (!section) continue
    const haystack = `${section.title}\n${section.body}`.toLowerCase()
    // Only backticked spans are treated as claims. A quoted term is often the
    // author's own characterisation of a section rather than something the
    // section says; describing an index as a copy is a fair account of an
    // indexing section that never uses the word. A code span names a concrete
    // artifact, so its absence means the reference points somewhere it should
    // not. Quoted terms are still checked, but reported as advisory.
    const hard = [...tail.matchAll(/`([^`\n]{2,40})`/g)].map((x) => x[1])
    const soft = [...tail.matchAll(/「([^」\n]{2,24})」/g)].map((x) => x[1])
    for (const [claim, severity] of [
      ...hard.map((c) => [c, 'error']),
      ...soft.map((c) => [c, 'advisory']),
    ]) {
      if (claim.includes('**') || claim.includes('$')) continue
      if (!haystack.includes(claim.toLowerCase())) {
        findings.push({
          path,
          line: 0,
          rule: `crossref-claim-missing${severity === 'advisory' ? '/advisory' : ''}`,
          match: `第 ${num} 節「${section.title.slice(0, 24)}」 does not contain 「${claim}」`,
          fix: 'point at the section that actually covers it',
        })
      }
    }
  }
}

// ── run ───────────────────────────────────────────────────────────────────
const files = collectFiles()
const findings = []

function readStagedOrDisk(rel) {
  try {
    if (isStaged && !rel.startsWith('/')) {
      return execSync(`git show :${rel}`, { cwd: ROOT, encoding: 'utf8' })
    }
    // join(ROOT, '/abs/path') would concatenate rather than resolve, so an
    // explicit path from the test suite has to be used as it is.
    return readFileSync(rel.startsWith('/') ? rel : join(ROOT, rel), 'utf8')
  } catch {
    return null
  }
}

// Every lesson's own section index, plus a lookup by unit number for
// cross-unit references.
const byUnit = new Map()
const texts = new Map()
for (const rel of files) {
  const text = readStagedOrDisk(rel)
  if (text === null) continue
  texts.set(rel, text)
  const unit = rel.match(/lessons\/(\d+)-/)
  if (unit && !byUnit.has(Number(unit[1]))) {
    byUnit.set(Number(unit[1]), sectionIndex(text))
  }
}

for (const [rel, text] of texts) {
  const lines = text.split('\n')
  checkEmphasis(lines, rel, findings)
  checkCallouts(lines, rel, findings)
  // Any file with at least two numbered sections can carry cross-references,
  // not only files under lessons/.
  if (sectionIndex(text).size >= 2) {
    checkCrossRefs(text, rel, sectionIndex(text), byUnit, findings)
  }
}

const seen = new Set()
const unique = findings.filter((f) => {
  const k = `${f.path}|${f.line}|${f.rule}|${f.match}`
  if (seen.has(k)) return false
  seen.add(k)
  return true
})
const errors = unique.filter((f) => !f.rule.endsWith('/advisory'))
const advisories = unique.filter((f) => f.rule.endsWith('/advisory'))

let current = ''
for (const f of [...errors, ...advisories]) {
  if (f.path !== current) {
    current = f.path
    console.log(`\n${current}:`)
  }
  const tag = f.rule.endsWith('/advisory') ? `${f.rule} (advisory)` : f.rule
  console.log(`  L${f.line} [${tag}] ${f.match}`)
  console.log(`    fix: ${f.fix}`)
}

if (errors.length === 0) {
  console.log(
    `\nCLEAN — ${files.length} file(s): emphasis parses, no nested Callouts, every backticked cross-reference claim is present.`
  )
  if (advisories.length) {
    console.log(
      `${advisories.length} advisory item(s) above: quoted terms, which are often paraphrase.`
    )
  }
  process.exit(0)
}
console.log(`\n${errors.length} error(s), ${advisories.length} advisory.`)
process.exit(1)
