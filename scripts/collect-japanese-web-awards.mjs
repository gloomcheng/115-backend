import fs from 'node:fs/promises'
import path from 'node:path'

const rounds = [6, 7, 8, 9, 10, 11, 12, 13]
const outputOption = process.argv.indexOf('--output')
const outputPath = path.resolve(
  outputOption >= 0
    ? process.argv[outputOption + 1]
    : '.agents/skills/course-curatorial-design/resources/japanese-web-awards.json'
)

if (outputOption >= 0 && !process.argv[outputOption + 1]) {
  throw new Error('Missing path after --output')
}

function text(html) {
  return html
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

const entries = []

for (const round of rounds) {
  const slug = String(round).padStart(2, '0')
  const response = await fetch(`https://award.dmi.jaa.or.jp/winner/gp${slug}c`)
  if (!response.ok) throw new Error(`Web Grand Prix ${round}: ${response.status}`)

  const html = await response.text()
  const pattern =
    /<h4>([\s\S]*?)<\/h4>[\s\S]*?<p class="site-award-name">([\s\S]*?)<\/p>[\s\S]*?<p class="site-link">([\s\S]*?)<\/p>/g

  for (const match of html.matchAll(pattern)) {
    entries.push({
      year: 2012 + round,
      title: text(match[1]),
      owner: text(match[2]),
      url: text(match[3]),
      source: `https://award.dmi.jaa.or.jp/winner/gp${slug}c`,
    })
  }
}

const uniqueEntries = [
  ...new Map(entries.map((entry) => [`${entry.year}|${entry.url}`, entry])).values(),
]

await fs.mkdir(path.dirname(outputPath), { recursive: true })
await fs.writeFile(
  outputPath,
  `${JSON.stringify(
    {
      schemaVersion: 1,
      source: 'Web Grand Prix corporate award archive',
      sourceArchive: 'https://award.dmi.jaa.or.jp/winner',
      years: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
      collectedAt: new Date().toISOString(),
      count: uniqueEntries.length,
      entries: uniqueEntries,
    },
    null,
    2
  )}\n`
)

console.log(
  `Collected ${uniqueEntries.length} unique award entries at ${path.relative(process.cwd(), outputPath)}.`
)
