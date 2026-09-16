import fs from 'node:fs'
import path from 'node:path'

/**
 * Two-paragraph reading-window audit.
 *
 * A window is made from adjacent learner-facing prose paragraphs.
 *
 * The audit is intentionally deterministic. It checks two editorial contracts:
 * 1. adjacent paragraphs share a visible concept or state an explicit bridge;
 * 2. first-use technical terms carry a local explanation.
 */

const LESSONS_DIR = path.resolve('src/content/lessons')

const STOP_WORDS = new Set([
  'about',
  'after',
  'also',
  'because',
  'been',
  'before',
  'being',
  'from',
  'have',
  'into',
  'just',
  'more',
  'only',
  'that',
  'their',
  'them',
  'then',
  'there',
  'these',
  'they',
  'this',
  'those',
  'through',
  'what',
  'when',
  'where',
  'which',
  'with',
  'your',
  'and',
  'for',
  'the',
  '有',
  '也',
  '不',
  '不能',
  '不要',
  '不是',
  '可以',
  '只是',
  '仍然',
  '以及',
  '這個',
  '這一',
  '這些',
  '一個',
  '每一',
  '目前',
  '之後',
  '如果',
  '因此',
  '所以',
])

const CONNECTIVE_PATTERNS = [
  /^(這|它|因此|所以|接著|下一|現在|到這裡|不論|既然|換句話說|同樣|也就是|假設|拿|依序|每次|最後|另外|從|當|在|觀察|執行|送出|收到|比較|注意|例如|除了)/,
  /(回到|沿著|對照|相同的|同一個|共同的|這條路|這一去一回)/,
]

const CONCEPT_CONTRACTS_BY_WEEK = {
  1: [
    {
      name: 'Method',
      term: /\bMethod\b/i,
      explanation: /(Method[^。\n]*(操作|動作|動詞)|(操作|動作|動詞)[^。\n]*Method)/i,
    },
    {
      name: 'Status Code',
      term: /\bStatus Code\b/i,
      explanation: /(Status Code[^。\n]*(狀態|數字|結果)|(狀態|數字|結果)[^。\n]*Status Code)/i,
    },
    {
      name: 'Header',
      term: /\bHeader\b/i,
      explanation: /(Header[^。\n]*(附加|欄位|資訊)|(附加|欄位|資訊)[^。\n]*Header)/i,
    },
    {
      name: 'Body',
      term: /\bBody\b/i,
      explanation: /(Body[^。\n]*(內容|訊息|資料)|(內容|訊息|資料)[^。\n]*Body)/i,
    },
    {
      name: 'reason phrase',
      term: /reason phrase/i,
      explanation: /(reason phrase[^。\n]*簡短文字|簡短文字[^。\n]*reason phrase)/i,
    },
  ],
  2: [
    {
      name: 'URI',
      term: /\bURI\b/,
      explanation: /(URI[^。\n]*(識別|總稱)|(識別|總稱)[^。\n]*URI)/i,
    },
    {
      name: 'URL',
      term: /\bURL\b/,
      explanation: /(URL[^。\n]*(定位|網址|主機)|(定位|網址|主機)[^。\n]*URL)/i,
    },
    {
      name: 'path',
      term: /\bpath\b/i,
      explanation: /(path[^。\n]*(路徑|位置|資源)|(路徑|位置|資源)[^。\n]*path)/i,
    },
    {
      name: 'query',
      term: /\bquery\b/i,
      explanation: /(query[^。\n]*(參數|\?)|(參數|\?)[^。\n]*query)/i,
    },
    {
      name: 'fragment',
      term: /\bfragment\b/i,
      explanation: /(fragment[^。\n]*(#|錨點|Client|不送)|(#|錨點|Client|不送)[^。\n]*fragment)/i,
    },
    {
      name: 'Header',
      term: /\bHeader\b/i,
      explanation: /(Header[^。\n]*(附加|欄位|描述)|(附加|欄位|描述)[^。\n]*Header)/i,
    },
    {
      name: 'Body',
      term: /\bBody\b/i,
      explanation: /(Body[^。\n]*(內容|本身)|(內容|本身)[^。\n]*Body)/i,
    },
  ],
}

function parseWeek(content) {
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---/)
  const week = frontmatter?.[1].match(/^week:\s*(\d+)/m)
  return week ? Number(week[1]) : null
}

function stripInlineMarkup(value) {
  return value
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<\/?[A-Za-z][^>]*>/g, ' ')
    .replace(/\{[^{}]*\}/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function collectParagraphs(content) {
  const lines = content.split('\n')
  const paragraphs = []
  let currentLines = []
  let startLine = null
  let hiddenBlock = null
  let inFrontmatter = false
  let inBibliography = false
  let pendingTerminalPrompt = false

  const flush = (endLine) => {
    const text = stripInlineMarkup(currentLines.join(' '))
    const isPureLinks = /^(\[[^\]]+\]\([^)]+\)\s*)+$/.test(text)
    if (text && text.length >= 12 && !/^來源[：:]/.test(text) && !isPureLinks) {
      paragraphs.push({ text, startLine, endLine })
    }
    currentLines = []
    startLine = null
    pendingTerminalPrompt = false
  }

  for (let index = 0; index < lines.length; index += 1) {
    const lineNumber = index + 1
    const rawLine = lines[index]
    const trimmedLine = rawLine.trim()

    if (lineNumber === 1 && trimmedLine === '---') {
      inFrontmatter = true
      continue
    }
    if (inFrontmatter) {
      if (trimmedLine === '---') inFrontmatter = false
      continue
    }
    if (/^import\s/.test(trimmedLine)) {
      flush(lineNumber - 1)
      continue
    }

    if (/^#{1,6}\s+(本單元使用的正本|參考資料|References|Sources)\b/i.test(trimmedLine)) {
      flush(lineNumber - 1)
      inBibliography = true
      continue
    }
    if (inBibliography) {
      if (/^#{1,6}\s/.test(trimmedLine)) inBibliography = false
      else continue
    }

    if (hiddenBlock) {
      if (trimmedLine.includes(`</${hiddenBlock}>`)) {
        if (hiddenBlock !== 'Terminal' || !pendingTerminalPrompt) {
          flush(lineNumber - 1)
        }
        hiddenBlock = null
      }
      continue
    }

    const hiddenStart = trimmedLine.match(/^<(Terminal|svg|Callout|FieldNote)\b/i)
    if (hiddenStart) {
      const tag = hiddenStart[1]
      const joined = currentLines.join(' ').trim()
      if (tag.toLowerCase() === 'terminal' && joined.length > 0 && /[：:]$/.test(joined)) {
        pendingTerminalPrompt = true
      } else {
        flush(lineNumber - 1)
      }
      if (!trimmedLine.includes(`</${tag}>`)) {
        hiddenBlock = tag
      } else {
        if (tag.toLowerCase() !== 'terminal' || !pendingTerminalPrompt) {
          flush(lineNumber - 1)
        }
      }
      continue
    }

    if (
      !trimmedLine ||
      /^#{1,6}\s/.test(trimmedLine) ||
      /^---+$/.test(trimmedLine) ||
      /^<(img|[A-Z][A-Za-z]+)\b[^>]*\/?>$/.test(trimmedLine)
    ) {
      if (!trimmedLine && currentLines.length > 0 && /[：:]$/.test(currentLines.join(' ').trim())) {
        continue
      }
      flush(lineNumber - 1)
      continue
    }

    if (/^(\[[^\]]+\]\([^)]+\)\s*)+$/.test(trimmedLine)) {
      flush(lineNumber - 1)
      continue
    }

    const listMatch = trimmedLine.match(/^([-*+]|\d+[.)])\s+(.*)/)
    if (listMatch) {
      const listContent = stripInlineMarkup(listMatch[2])
      if (listContent) {
        if (startLine === null) startLine = lineNumber
        currentLines.push(listContent)
      }
      continue
    }

    const textLine = stripInlineMarkup(rawLine)
    if (!textLine) {
      flush(lineNumber - 1)
      continue
    }
    if (startLine === null) startLine = lineNumber
    currentLines.push(textLine)
  }

  flush(lines.length)
  return paragraphs
}

function tokenize(value) {
  const tokens = new Set()
  for (const match of value.toLowerCase().matchAll(/[a-z][a-z0-9_/-]{1,}/g)) {
    if (!STOP_WORDS.has(match[0])) tokens.add(match[0])
  }
  for (const match of value.matchAll(/\b(?:[1-5]xx|[1-5]\d{2})\b/g)) {
    tokens.add(match[0])
  }

  for (const match of value.matchAll(/[\u3400-\u9fff]+/g)) {
    const segment = match[0]
    for (let index = 0; index < segment.length - 1; index += 1) {
      const bigram = segment.slice(index, index + 2)
      if (!STOP_WORDS.has(bigram)) tokens.add(bigram)
    }
  }
  return tokens
}

function sharedTerms(first, second) {
  const firstTerms = tokenize(first)
  return [...tokenize(second)].filter((term) => firstTerms.has(term))
}

function hasExplicitBridge(text) {
  return CONNECTIVE_PATTERNS.some((pattern) => pattern.test(text))
}

function auditWindows(paragraphs) {
  const findings = []
  for (let index = 1; index < paragraphs.length; index += 1) {
    const previous = paragraphs[index - 1]
    const current = paragraphs[index]
    const overlap = sharedTerms(previous.text, current.text)
    const explicitBridge = hasExplicitBridge(current.text)

    if (overlap.length === 0 && !explicitBridge) {
      const location = `${previous.startLine}-${current.endLine}`
      findings.push(
        {
          type: 'window',
          direction: 'forward',
          pair_location: location,
          startLine: previous.startLine,
          endLine: current.endLine,
          message:
            'The lower paragraph does not continue a visible question, operation, or consequence from the upper paragraph.',
          expected_continuation_or_missing_premise:
            'Name the unresolved question or next operation created by the upper paragraph.',
          reader_consequence: 'A reader cannot tell why the lower paragraph follows.',
          repair:
            'Add a concrete bridge or reorder the paragraphs so the next operation is motivated.',
          source_boundary:
            'Claim needs editorial repair; verify any new factual bridge against the lesson source.',
          previous: previous.text,
          current: current.text,
          location,
        },
        {
          type: 'window',
          direction: 'backward',
          pair_location: location,
          startLine: previous.startLine,
          endLine: current.endLine,
          message:
            'The lower paragraph requires a premise that is not supplied by the upper paragraph.',
          expected_continuation_or_missing_premise:
            "Identify the lower paragraph's first required term, actor, or causal link.",
          reader_consequence:
            'A reader must use a heading or distant context to understand the lower paragraph.',
          repair:
            'Define the missing premise in the upper paragraph or move the dependent paragraph later.',
          source_boundary:
            'Claim needs editorial repair; do not import definitions from a later section.',
          previous: previous.text,
          current: current.text,
          location,
        }
      )
    }
  }
  return findings
}

function auditConceptContracts(week, content, paragraphs) {
  const contracts = CONCEPT_CONTRACTS_BY_WEEK[week] ?? []
  const fullText = content
  return contracts.flatMap((contract) => {
    const firstUse = fullText.search(contract.term)
    if (firstUse === -1 || contract.explanation.test(fullText.slice(firstUse))) return []
    const paragraph = paragraphs.find((item) => contract.term.test(item.text))
    return [
      {
        type: 'concept',
        direction: 'backward',
        pair_location: `${paragraph?.startLine ?? '?'} -> ${paragraph?.endLine ?? '?'}`,
        startLine: paragraph?.startLine ?? '?',
        endLine: paragraph?.endLine ?? '?',
        message: `First use of ${contract.name} has no local explanation.`,
        expected_continuation_or_missing_premise: `Define ${contract.name} with a concrete referent and purpose before relying on it.`,
        reader_consequence: `The reader sees ${contract.name} as a label instead of an operation or object.`,
        repair: `Add the smallest source-accurate definition at the first use.`,
        source_boundary: 'Verify the definition against the relevant protocol or course source.',
      },
    ]
  })
}

function fileListForWeek(week) {
  if (!fs.existsSync(LESSONS_DIR)) return []
  return fs
    .readdirSync(LESSONS_DIR)
    .filter((fileName) => /\.mdx?$/.test(fileName))
    .map((fileName) => path.join(LESSONS_DIR, fileName))
    .filter((filePath) => parseWeek(fs.readFileSync(filePath, 'utf8')) === week)
}

function allLessonFiles() {
  if (!fs.existsSync(LESSONS_DIR)) return []
  return fs
    .readdirSync(LESSONS_DIR)
    .filter((fileName) => /\.mdx?$/.test(fileName))
    .map((fileName) => path.join(LESSONS_DIR, fileName))
    .sort((a, b) => {
      const weekA = parseWeek(fs.readFileSync(a, 'utf8')) ?? 999
      const weekB = parseWeek(fs.readFileSync(b, 'utf8')) ?? 999
      return weekA - weekB
    })
}

function parseArgs() {
  const weekIndex = process.argv.indexOf('--week')
  if (weekIndex !== -1 && process.argv[weekIndex + 1]) {
    const value = Number(process.argv[weekIndex + 1])
    if (!Number.isInteger(value) || value < 1) {
      console.error('Usage: node scripts/reading-window-harness.mjs [--week N]')
      process.exit(2)
    }
    return { mode: 'week', week: value }
  }
  return { mode: 'all' }
}

function run() {
  const config = parseArgs()
  const files = config.mode === 'week' ? fileListForWeek(config.week) : allLessonFiles()

  console.log(
    config.mode === 'week'
      ? `Running two-paragraph reading-window audit for week ${config.week}...`
      : 'Running two-paragraph reading-window audit for all lessons...'
  )

  if (files.length === 0) {
    console.error(`No lesson files found in ${LESSONS_DIR}.`)
    process.exit(1)
  }

  let totalWindows = 0
  const findings = []

  for (const filePath of files) {
    const content = fs.readFileSync(filePath, 'utf8')
    const week = parseWeek(content) ?? 1
    const paragraphs = collectParagraphs(content)
    const windows = Math.max(0, paragraphs.length - 1)
    totalWindows += windows

    const fileFindings = [
      ...auditWindows(paragraphs),
      ...auditConceptContracts(week, content, paragraphs),
    ]

    if (paragraphs.length < 2) {
      fileFindings.push({
        type: 'window',
        direction: 'forward',
        pair_location: `${path.basename(filePath)}:not-enough-paragraphs`,
        startLine: '?',
        endLine: '?',
        message:
          'The lesson does not expose at least two learner-facing prose paragraphs for a window audit.',
        expected_continuation_or_missing_premise:
          "Mark the lesson's actual reading path and provide an adjacent pair.",
        reader_consequence:
          'The continuity gate cannot inspect whether one paragraph leads to the next.',
        repair:
          'Add or mark the main prose paragraphs; do not satisfy the gate with a heading or sidebar.',
        source_boundary: 'Not applicable; this is an audit coverage failure.',
      })
    }
    findings.push(...fileFindings.map((finding) => ({ ...finding, filePath })))
    console.log(
      `  ${path.basename(filePath)} (week ${week}): ${paragraphs.length} paragraphs, ${windows} windows`
    )
  }

  for (const finding of findings) {
    const location = `${path.relative(process.cwd(), finding.filePath)}:${finding.startLine}-${finding.endLine}`
    console.error(`  ✗ ${location} [${finding.direction}] ${finding.message}`)
    console.error(`    pair_location: ${finding.pair_location}`)
    console.error(
      `    expected_continuation_or_missing_premise: ${finding.expected_continuation_or_missing_premise}`
    )
    console.error(`    reader_consequence: ${finding.reader_consequence}`)
    console.error(`    repair: ${finding.repair}`)
    console.error(`    source_boundary: ${finding.source_boundary}`)
    if (finding.type === 'window') {
      console.error(`    previous: ${finding.previous}`)
      console.error(`    current:  ${finding.current}`)
    }
  }

  if (findings.length > 0) {
    console.error(
      `Reading-window audit failed: ${findings.length} finding(s) across ${totalWindows} windows.`
    )
    process.exit(1)
  }
  console.log(
    `✓ Reading-window audit passed: ${totalWindows} adjacent windows across ${files.length} lesson(s) are connected and locally explained.`
  )
}

run()
