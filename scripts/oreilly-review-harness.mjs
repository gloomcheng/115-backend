import fs from 'node:fs'
import path from 'node:path'

/**
 * O'Reilly Editorial Review Harness
 * Validates lesson MDX content against the O'Reilly Editorial Standard:
 * 1. Topic Atomicity & Header Structure (no duplicate titles, standard unit nomenclature)
 * 2. Visual Component & ELI5 Diagram Presence
 * 3. Observable Proofs (curl / terminal verification blocks)
 * 4. Safe Forward References (Advanced terms like JWT/Token/Cookie must be anchored in Callouts)
 */

const LESSONS_DIR = path.resolve('src/content/lessons')
const FIELD_NOTES_PATH = path.resolve('docs/industry-field-notes.json')
const LESSON_TOPICS_PATH = path.resolve('docs/lesson-industry-topics.json')
const lessonTopics = fs.existsSync(LESSON_TOPICS_PATH)
  ? JSON.parse(fs.readFileSync(LESSON_TOPICS_PATH, 'utf8'))
  : {}

function lessonTags(content) {
  const tags = new Set()
  const rules = [
    ['http', /HTTP|Request|Response|curl/i],
    ['status-code', /Status Code|\b[1-5]xx\b|\b[1-5][0-9]{2}\b/i],
    ['browser', /Browser|瀏覽器/i],
    ['security', /JWT|Token|Cookie|認證|權限|安全/i],
    ['payments', /Payment|付款|支付|402/i],
    ['agents', /Agent|代理人/i],
  ]
  for (const [tag, pattern] of rules) {
    if (pattern.test(content)) tags.add(tag)
  }
  return tags
}

function fieldNoteSuggestions(content, lessonId) {
  if (!fs.existsSync(FIELD_NOTES_PATH)) return []
  const cache = JSON.parse(fs.readFileSync(FIELD_NOTES_PATH, 'utf8'))
  const tags = new Set(lessonTopics[lessonId] ?? lessonTags(content))
  const discoveries = (cache.discoveries ?? [])
    .map((item) => ({
      ...item,
      matchCount: item.tags.filter((tag) => tags.has(tag)).length,
      titleMatchCount: (item.titleTags ?? []).filter((tag) => tags.has(tag)).length,
    }))
    .filter(
      (item) => item.titleMatchCount >= 1 && item.matchCount >= 2 && !content.includes(item.url)
    )
    .sort((a, b) => {
      const tagDifference = b.matchCount - a.matchCount
      if (tagDifference !== 0) return tagDifference
      return Date.parse(b.publishedAt || 0) - Date.parse(a.publishedAt || 0)
    })
    .slice(0, 3)
    .map((item) => ({
      suggestion: item.title,
      source: `${item.source} (${item.sourceType})`,
      url: item.url,
      verificationRequired: item.verificationRequired,
    }))

  if (discoveries.length > 0) return discoveries

  return (cache.items ?? [])
    .filter((item) => item.tags.some((tag) => tags.has(tag)) && !content.includes(item.url))
    .sort(
      (a, b) =>
        b.tags.filter((tag) => tags.has(tag)).length - a.tags.filter((tag) => tags.has(tag)).length
    )
    .slice(0, 3)
}

function checkLesson(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const fileName = path.basename(filePath)
  const errors = []
  const warnings = []

  // Check 1: Frontmatter title vs MDX body h1 duplication
  const titleMatch = content.match(/title:\s*["']([^"']+)["']/)
  if (titleMatch) {
    const frontmatterTitle = titleMatch[1]
    const h1Match = content.match(/^#\s+(.+)$/m)
    if (h1Match && h1Match[1].trim() === frontmatterTitle.trim()) {
      errors.push(
        `Duplicate H1 header found in body: "${h1Match[1]}". Remove H1 from MDX since the layout header already renders it.`
      )
    }
  }

  // Check 2: Legacy week naming prohibition (strictly use unit nomenclature)
  const legacyWeekRegex = /第\s*[0-9一二三四五六七八九十]+\s*週/g
  const weekMatches = content.match(legacyWeekRegex)
  if (weekMatches) {
    errors.push(
      `Found legacy week references (${weekMatches.join(', ')}). The course is strictly organized into 16 units.`
    )
  }

  // Check 3: Observable Proof presence (curl / terminal commands)
  const hasTerminal =
    content.includes('<Terminal') || content.includes('```bash') || content.includes('curl ')
  if (!hasTerminal) {
    errors.push(
      'No observable proof found. Every lesson must contain runnable terminal commands (e.g., curl -v).'
    )
  }

  // Check 4: Visual Illustration / ELI5 diagram presence
  const hasVisual =
    content.includes('Visual') ||
    content.includes('Diagram') ||
    content.includes('Cards') ||
    content.includes('House') ||
    content.includes('<svg') ||
    /!\[[^\]]*ELI5[^\]]*\]\([^)]+\)/i.test(content) ||
    /<img\b(?=[^>]*\balt=["'][^"']*ELI5[^"']*["'])[^>]*>/i.test(content)
  if (!hasVisual) {
    errors.push(
      'No ELI5 illustration found. Add a visual component, SVG, or image with an ELI5 alt description.'
    )
  }

  // Check 5: Forward References Safety (e.g. JWT / Token / Cookie in early lessons should be anchored in Callouts)
  const forwardTerms = ['JWT', 'Token', 'Cookie', 'Session']
  for (const term of forwardTerms) {
    if (
      content.includes(term) &&
      !content.includes('<Callout') &&
      !content.includes('<GlossaryTerm')
    ) {
      warnings.push(
        `Term "${term}" appears without an anchoring <Callout> or <GlossaryTerm>. Forward references should be explicit.`
      )
    }
  }

  const lessonId = fileName.replace(/\.mdx?$/, '')
  return { fileName, errors, warnings, suggestions: fieldNoteSuggestions(content, lessonId) }
}

function run() {
  console.log("Running O'Reilly Editorial Review Harness...")
  if (!fs.existsSync(LESSONS_DIR)) {
    console.log(`Directory ${LESSONS_DIR} does not exist. Skipping.`)
    return
  }

  const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.md') || f.endsWith('.mdx'))
  let totalErrors = 0
  let totalWarnings = 0

  for (const f of files) {
    const fullPath = path.join(LESSONS_DIR, f)
    const result = checkLesson(fullPath)
    console.log(`\n📄 Reviewing ${result.fileName}:`)

    if (result.errors.length === 0 && result.warnings.length === 0) {
      console.log(
        "  ✓ Passed all O'Reilly Editorial Review checks (Atomic, Visual, Observable, Clean)."
      )
    }

    for (const w of result.warnings) {
      console.log(`  ⚠ WARNING: ${w}`)
      totalWarnings++
    }

    for (const e of result.errors) {
      console.log(`  ✗ ERROR: ${e}`)
      totalErrors++
    }

    for (const suggestion of result.suggestions) {
      console.log(`  SUGGESTION: ${suggestion.suggestion}`)
      console.log(`    Source: ${suggestion.source} — ${suggestion.url}`)
      if (suggestion.verificationRequired) {
        console.log('    Verification: required before adding this item to course copy')
      }
    }
  }

  console.log(
    `\nO'Reilly Editorial Review finished: ${totalErrors} errors, ${totalWarnings} warnings.`
  )
  if (totalErrors > 0) {
    process.exit(1)
  }
}

run()
