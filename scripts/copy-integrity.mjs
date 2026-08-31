import fs from 'node:fs'
import path from 'node:path'

const baselinePath = path.resolve('docs/copy-baseline.json')
const distPath = path.resolve('dist')

function collectRoutes(directory = distPath) {
  const routes = []
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolutePath = path.join(directory, entry.name)
    if (entry.isDirectory()) routes.push(...collectRoutes(absolutePath))
    else if (entry.name === 'index.html') {
      routes.push(path.relative(distPath, absolutePath).split(path.sep).join('/'))
    }
  }
  return routes.sort()
}

const routes = collectRoutes()

function visibleTokens(file) {
  const html = fs.readFileSync(path.resolve(distPath, file), 'utf8')
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
const baselineRoutes = Object.keys(baseline).sort()
if (JSON.stringify(baselineRoutes) !== JSON.stringify(routes)) {
  const added = routes.filter((route) => !baselineRoutes.includes(route))
  const removed = baselineRoutes.filter((route) => !routes.includes(route))
  console.error(
    `Rendered route set changed. Added: ${added.join(', ') || 'none'}. Removed: ${removed.join(', ') || 'none'}.`
  )
  console.error(
    'Run `npm run copy:baseline` only after the route and visible copy changes are approved.'
  )
  process.exit(1)
}

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
