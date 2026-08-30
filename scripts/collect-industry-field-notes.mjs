import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

const verificationPath = path.resolve('docs/industry-field-note-sources.json')
const discoveryPath = path.resolve('docs/industry-discovery-sources.json')
const threadsPath = path.resolve('docs/industry-threads-inbox.json')
const cachePath = path.resolve('docs/industry-field-notes.json')

const verificationSources = JSON.parse(fs.readFileSync(verificationPath, 'utf8'))
const discoverySources = JSON.parse(fs.readFileSync(discoveryPath, 'utf8'))
const threadsInbox = JSON.parse(fs.readFileSync(threadsPath, 'utf8'))
const previous = fs.existsSync(cachePath)
  ? JSON.parse(fs.readFileSync(cachePath, 'utf8'))
  : { items: [], discoveries: [] }
const previousVerification = new Map((previous.items ?? []).map((item) => [item.id, item]))

function decode(value) {
  return value
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&amp;/g, '&')
    .replace(/&quot;|&#34;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#x2F;/gi, '/')
    .replace(/\s+/g, ' ')
    .trim()
}

function extract(html, pattern) {
  const match = html.match(pattern)
  return match ? decode(match[1].replace(/<[^>]+>/g, ' ')) : ''
}

function inferTags(value) {
  const rules = [
    ['http', /HTTP|API|網頁|Web|協定|protocol/i],
    ['status-code', /status code|狀態碼|HTTP\s*[1-5][0-9]{2}|\b[1-5]xx\b/i],
    ['browser', /browser|瀏覽器|Chrome|Firefox/i],
    ['agents', /AI agent|agentic|代理型|代理人|智慧代理/i],
    ['payments', /payment|支付|付款|金流|checkout|x402|AP2|ACP/i],
    ['database', /database|資料庫|SQLite|PostgreSQL|MySQL/i],
    ['security', /security|資安|漏洞|CVE|攻擊|勒索|身分驗證/i],
    ['deployment', /cloud|雲端|Docker|container|Kubernetes|部署/i],
  ]
  return rules.filter(([, pattern]) => pattern.test(value)).map(([tag]) => tag)
}

function rssItems(xml, source) {
  return [...xml.matchAll(/<item\b[^>]*>([\s\S]*?)<\/item>/gi)]
    .slice(0, 40)
    .map((match, index) => {
      const item = match[1]
      const title = extract(item, /<title[^>]*>([\s\S]*?)<\/title>/i)
      const url = extract(item, /<link[^>]*>([\s\S]*?)<\/link>/i)
      const description = extract(item, /<description[^>]*>([\s\S]*?)<\/description>/i)
      const publishedAt = extract(item, /<pubDate[^>]*>([\s\S]*?)<\/pubDate>/i)
      return {
        id: `${source.id}-${index}-${Buffer.from(url).toString('base64url').slice(0, 12)}`,
        discoverySourceId: source.id,
        source: source.source,
        sourceType: 'taiwan-tech-news',
        region: source.region,
        url,
        title,
        publishedAt,
        titleTags: inferTags(title),
        tags: inferTags(`${title} ${description}`),
        verificationRequired: true,
      }
    })
    .filter((item) => item.title && item.url && item.tags.length > 0)
}

async function fetchText(url) {
  const response = await fetch(url, {
    headers: { 'user-agent': '115-backend-course-research/1.0' },
    signal: AbortSignal.timeout(15000),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.text()
}

const items = []
const discoveries = []
const failures = []

for (const source of verificationSources) {
  try {
    const html = await fetchText(source.url)
    const title = extract(html, /<title[^>]*>([\s\S]*?)<\/title>/i)
    const description =
      extract(html, /<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["'][^>]*>/i) ||
      extract(html, /<meta[^>]+content=["']([^"']+)["'][^>]+name=["']description["'][^>]*>/i)
    items.push({ ...source, title, description, fetchedAt: new Date().toISOString() })
    console.log(`Verified ${source.id}: ${title || source.url}`)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    const cached = previousVerification.get(source.id)
    if (cached) items.push({ ...cached, refreshError: message })
    failures.push(`${source.id}: ${message}`)
  }
}

for (const source of discoverySources) {
  try {
    const xml = await fetchText(source.url)
    const found = rssItems(xml, source)
    discoveries.push(...found)
    console.log(`Discovered ${found.length} tagged items from ${source.source}`)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    const cached = (previous.discoveries ?? []).filter(
      (item) => item.discoverySourceId === source.id
    )
    discoveries.push(...cached)
    failures.push(`${source.id}: ${message}`)
  }
}

for (const entry of threadsInbox.items ?? []) {
  discoveries.push({
    ...entry,
    source: 'Threads',
    sourceType: 'threads',
    region: 'TW',
    verificationRequired: !entry.verificationUrl,
  })
}

fs.writeFileSync(
  cachePath,
  `${JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      items,
      discoveries,
      threads: {
        mode: threadsInbox.mode,
        watchQueries: threadsInbox.watchQueries,
        itemCount: threadsInbox.items?.length ?? 0,
      },
    },
    null,
    2
  )}\n`
)

const formatResult = spawnSync('npx', ['biome', 'format', '--write', cachePath], {
  stdio: 'inherit',
})
if (formatResult.status !== 0) process.exit(formatResult.status ?? 1)

if ((threadsInbox.items?.length ?? 0) === 0) {
  console.log('Threads inbox is empty; public posts require manual URL intake or API credentials.')
}

if (failures.length > 0) {
  console.warn('Some sources could not be refreshed:')
  failures.forEach((failure) => {
    console.warn(`- ${failure}`)
  })
}

if (items.length !== verificationSources.length) process.exit(1)
