import fs from 'node:fs'
import path from 'node:path'

const roots = ['src/components', 'src/content', 'src/data', 'src/layouts', 'src/pages']
const extensions = new Set(['.astro', '.js', '.jsx', '.json', '.md', '.mdx', '.ts', '.tsx'])
const emojiPattern = /[\u2600-\u27bf]|[\u{1f000}-\u{1faff}]/gu
const failures = []

function collectFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(directory, entry.name)
    if (entry.isDirectory()) return collectFiles(target)
    return extensions.has(path.extname(entry.name)) ? [target] : []
  })
}

for (const root of roots) {
  for (const file of collectFiles(root)) {
    const lines = fs.readFileSync(file, 'utf8').split('\n')
    lines.forEach((line, index) => {
      const matches = [...line.matchAll(emojiPattern)]
      for (const match of matches) {
        failures.push(`${file}:${index + 1} contains emoji ${JSON.stringify(match[0])}`)
      }
    })
  }
}

if (failures.length > 0) {
  console.error('Emoji and icon-set check failed:')
  failures.forEach((failure) => {
    console.error(`- ${failure}`)
  })
  console.error('Use the installed Lucide icon set for semantic UI icons.')
  process.exit(1)
}

console.log('Emoji and icon-set check passed.')
