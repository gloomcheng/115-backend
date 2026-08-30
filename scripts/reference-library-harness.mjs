import fs from 'node:fs'
import path from 'node:path'

const libraryPath = path.resolve(
  '.agents/skills/course-curatorial-design/resources/japanese-web-awards.json'
)
const errors = []

if (!fs.existsSync(libraryPath)) {
  errors.push(`Missing reference library: ${libraryPath}`)
} else {
  const library = JSON.parse(fs.readFileSync(libraryPath, 'utf8'))
  if (library.schemaVersion !== 1) errors.push('Unsupported reference library schema.')
  if (!Array.isArray(library.years) || library.years.length < 8)
    errors.push('Reference library must cover at least eight award years.')
  if (!Array.isArray(library.entries) || library.entries.length < 100)
    errors.push('Reference library must contain at least 100 entries.')
  if (library.count !== library.entries?.length)
    errors.push('Reference library count does not match entries.')
  if (!library.collectedAt || Number.isNaN(Date.parse(library.collectedAt)))
    errors.push('Reference library has no valid collectedAt value.')

  const seen = new Set()
  for (const entry of library.entries ?? []) {
    if (!entry.title || !entry.owner || !entry.url || !entry.source || !entry.year) {
      errors.push('Reference library has an incomplete entry.')
      break
    }
    if (!entry.source.startsWith('https://award.dmi.jaa.or.jp/winner/gp')) {
      errors.push(`Reference entry has an unapproved source: ${entry.source}`)
      break
    }
    const key = `${entry.year}|${entry.url}`
    if (seen.has(key)) {
      errors.push(`Reference library has a duplicate: ${key}`)
      break
    }
    seen.add(key)
  }
}

if (errors.length > 0) {
  console.error('Reference library check failed:')
  errors.forEach((error) => {
    console.error(`- ${error}`)
  })
  process.exit(1)
}

console.log('Reference library check passed.')
