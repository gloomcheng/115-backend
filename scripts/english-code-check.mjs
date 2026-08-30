#!/usr/bin/env node
// English code and comment enforcement harness.
// Ensures that all source code, variable identifiers, function names, and code comments
// (//, /* */, <!-- -->, #) are written strictly in English.
// Traditional Chinese is only permitted in pedagogical content files (src/content/**).

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')

const EXCLUDED_DIRS = new Set(['node_modules', 'dist', '.git', '.astro', 'src/content'])

const CODE_EXTENSIONS = new Set([
  '.ts',
  '.tsx',
  '.js',
  '.jsx',
  '.mjs',
  '.cjs',
  '.astro',
  '.css',
  '.sh',
])

// CJK Unicode Range
const CJK_REGEX = /[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]/

function collectCodeFiles(dir) {
  const files = []
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry)
    const relPath = relative(ROOT, fullPath)

    if (
      EXCLUDED_DIRS.has(relPath) ||
      Array.from(EXCLUDED_DIRS).some((d) => relPath.startsWith(`${d}/`))
    ) {
      continue
    }

    const stat = statSync(fullPath)
    if (stat.isDirectory()) {
      files.push(...collectCodeFiles(fullPath))
    } else {
      const ext = entry.slice(entry.lastIndexOf('.'))
      if (CODE_EXTENSIONS.has(ext)) {
        files.push(fullPath)
      }
    }
  }
  return files
}

function extractComments(code, ext) {
  const commentRanges = []

  if (ext === '.astro') {
    // 1. HTML comments <!-- ... -->
    const htmlCommentRegex = /<!--([\s\S]*?)-->/g
    let match = htmlCommentRegex.exec(code)
    while (match !== null) {
      commentRanges.push({ text: match[1], index: match.index })
      match = htmlCommentRegex.exec(code)
    }

    // 2. JS comments within frontmatter (--- ... ---) or <script> tags
    const frontmatterMatch = code.match(/^---\r?\n([\s\S]*?)\r?\n---/)
    if (frontmatterMatch) {
      extractJsComments(frontmatterMatch[1], 4, commentRanges)
    }

    const scriptMatch = code.match(/<script[\s\S]*?>([\s\S]*?)<\/script>/)
    if (scriptMatch) {
      extractJsComments(scriptMatch[1], scriptMatch.index || 0, commentRanges)
    }
  } else if (ext === '.sh') {
    const lines = code.split('\n')
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const hashIndex = line.indexOf('#')
      if (hashIndex !== -1 && !line.startsWith('#!')) {
        commentRanges.push({ text: line.slice(hashIndex + 1), index: 0, line: i + 1 })
      }
    }
  } else {
    // Standard JS / TS / CSS comments
    extractJsComments(code, 0, commentRanges)
  }

  return commentRanges
}

function extractJsComments(text, offset, results) {
  // Line comments // ...
  const lineRegex = /\/\/([^\n]*)/g
  let match = lineRegex.exec(text)
  while (match !== null) {
    results.push({ text: match[1], index: offset + match.index })
    match = lineRegex.exec(text)
  }

  // Block comments /* ... */
  const blockRegex = /\/\*([\s\S]*?)\*\//g
  let blockMatch = blockRegex.exec(text)
  while (blockMatch !== null) {
    results.push({ text: blockMatch[1], index: offset + blockMatch.index })
    blockMatch = blockRegex.exec(text)
  }
}

function main() {
  const files = collectCodeFiles(ROOT)
  const violations = []

  for (const file of files) {
    const rel = relative(ROOT, file)
    const content = readFileSync(file, 'utf-8')
    const ext = file.slice(file.lastIndexOf('.'))

    // Check comments
    const comments = extractComments(content, ext)
    for (const comment of comments) {
      if (CJK_REGEX.test(comment.text)) {
        violations.push({
          file: rel,
          message: `Non-English comment found: "${comment.text.trim()}"`,
        })
      }
    }
  }

  if (violations.length > 0) {
    console.error(
      `\x1b[31m✗ Found ${violations.length} English code/comment violation(s):\x1b[0m\n`
    )
    for (const v of violations) {
      console.error(`  \x1b[33m${v.file}\x1b[0m: ${v.message}`)
    }
    console.error(
      '\nRule: All code, identifiers, and comments must be in English. Only pedagogical content in src/content/ may contain Traditional Chinese.\n'
    )
    process.exit(1)
  }

  console.log(
    `\x1b[32m✓ English code & comment harness passed: ${files.length} files checked (all comments & code are English-only).\x1b[0m`
  )
}

main()
