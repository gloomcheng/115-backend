#!/usr/bin/env node
// Proves the render-integrity guard fires. A guard that has never been seen
// to fail is not evidence of anything.

import { execFileSync } from 'node:child_process'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..', '..')
const GUARD = join(ROOT, 'scripts', 'render-integrity-harness.mjs')

const CASES = [
  {
    name: 'closing ** after punctuation before a CJK character',
    source: [
      '正常的一段，粗體是 **粗體** 這樣。',
      '',
      '壞的：一句話結束了。**後面緊接中文，**這樣。',
    ].join('\n'),
    expect: 'emphasis-unparsed/closing-after-punctuation',
  },
  {
    // Two delimiters on the line, matching how this actually appears in unit
    // 04. A line with a single ** is not flagged: bold may legitimately span
    // lines within a paragraph, so a lone delimiter proves nothing.
    name: 'opening ** followed by a space',
    source: [
      '你會自己動手——** 先加兩筆路由，再用你寫的那張表去預測結果。**',
      '',
      '結尾 **粗體** 這樣。',
    ].join('\n'),
    expect: 'emphasis-unparsed/opening-then-space',
  },
  {
    name: 'opening ** followed by CJK punctuation after a CJK character',
    source: ['而 是**「某個引號開頭的粗體」**。', '', '結尾 **粗體** 這樣。'].join('\n'),
    expect: 'emphasis-unparsed/opening-then-punctuation',
  },
  {
    name: 'Callout nested inside a Callout',
    source: [
      '<Callout type="important" title="外層">',
      '  外層內容。',
      '',
      '  <Callout type="warning" title="內層">',
      '    內層內容。',
      '  </Callout>',
      '</Callout>',
    ].join('\n'),
    expect: 'callout-nested',
  },
  {
    name: 'stray closing Callout tag',
    source: ['一段正文。', '</Callout>'].join('\n'),
    expect: 'callout-unbalanced',
  },
  {
    name: 'backticked cross-reference claim absent from the target section',
    source: [
      '## 01. 標題',
      '',
      '第 02 節那個 `PUT` 會怎樣。',
      '',
      '## 02. 別的標題',
      '',
      '這一節完全沒有提到那個 method。',
    ].join('\n'),
    expect: 'crossref-claim-missing',
  },
  {
    name: 'svg without a desc',
    source: [
      '<svg viewBox="0 0 10 10" role="img">',
      '  <title id="a">一個足夠長的圖說標題</title>',
      '  <rect width="10" height="10" />',
      '</svg>',
    ].join('\n'),
    expect: 'diagram-missing-desc',
  },
  {
    name: 'svg whose title is a label rather than a claim',
    source: [
      '<svg viewBox="0 0 10 10" role="img">',
      '  <title id="a">圖</title>',
      '  <desc id="b">一段足夠長的圖說內容，說明這張圖在論證什麼。</desc>',
      '  <rect width="10" height="10" />',
      '</svg>',
    ].join('\n'),
    expect: 'diagram-thin-claim',
  },
]

const dir = mkdtempSync(join(tmpdir(), 'render-integrity-'))
let failed = 0

try {
  for (const c of CASES) {
    const file = join(dir, 'sample.mdx')
    writeFileSync(file, c.source, 'utf8')
    let out = ''
    let code = 0
    try {
      out = execFileSync('node', [GUARD, '--files', file], { encoding: 'utf8' })
    } catch (e) {
      out = (e.stdout ?? '') + (e.stderr ?? '')
      code = e.status ?? 1
    }
    const fired = out.includes(c.expect)
    const ok = fired && code !== 0
    if (!ok) failed++
    console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${c.name}`)
    if (!ok) {
      console.log(`        expected rule: ${c.expect}`)
      console.log(`        exit: ${code}`)
      console.log(`        output: ${out.trim().split('\n').slice(0, 4).join(' | ')}`)
    }
  }
} finally {
  rmSync(dir, { recursive: true, force: true })
}

console.log(`\n${CASES.length - failed}/${CASES.length} guard tests passed`)
process.exit(failed ? 1 : 0)
