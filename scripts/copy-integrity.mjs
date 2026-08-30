import fs from 'node:fs'
import path from 'node:path'

const baselinePath = path.resolve('docs/copy-baseline.json')
const routes = [
  'index.html',
  'book/index.html',
  'glossary/index.html',
  'preparation/index.html',
  'lessons/01-http/index.html',
]

function visibleTokens(file) {
  const html = fs.readFileSync(path.resolve('dist', file), 'utf8')
  const text = html
    .replace(/<script[\s\S]*?<\/script>/g, '')
    .replace(/<style[\s\S]*?<\/style>/g, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim()
  const counts = new Map()
  for (const [token] of text.matchAll(/[^\s]+/g)) {
    if (/^[/.·]+$/.test(token)) continue
    counts.set(token, (counts.get(token) ?? 0) + 1)
  }
  return Object.fromEntries([...counts.entries()].sort(([a], [b]) => a.localeCompare(b)))
}

const snapshot = Object.fromEntries(routes.map((route) => [route, visibleTokens(route)]))

if (process.argv.includes('--record')) {
  fs.writeFileSync(baselinePath, `${JSON.stringify(snapshot, null, 2)}\n`)
  console.log(`Recorded copy baseline for ${routes.length} routes.`)
  process.exit(0)
}

if (!fs.existsSync(baselinePath)) {
  console.error(
    'Missing docs/copy-baseline.json. Run `npm run copy:baseline` after an approved copy review.'
  )
  process.exit(1)
}

const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf8'))
const changed = routes.filter(
  (route) => JSON.stringify(baseline[route]) !== JSON.stringify(snapshot[route])
)

if (changed.length > 0) {
  console.error(`Visible copy changed on: ${changed.join(', ')}`)
  for (const route of changed) {
    const keys = new Set([
      ...Object.keys(baseline[route] ?? {}),
      ...Object.keys(snapshot[route] ?? {}),
    ])
    const differences = [...keys]
      .filter((token) => (baseline[route]?.[token] ?? 0) !== (snapshot[route]?.[token] ?? 0))
      .map((token) => ({
        token,
        expected: baseline[route]?.[token] ?? 0,
        actual: snapshot[route]?.[token] ?? 0,
      }))
    console.error(`${route}: ${JSON.stringify(differences)}`)
  }
  process.exit(1)
}

console.log(`Copy integrity passed for ${routes.length} routes.`)
