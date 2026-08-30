import fs from 'node:fs'
import path from 'node:path'

const distDirectory = path.resolve('dist')
const pagesBase = '/115-backend/'

function collectHtmlFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name)
    if (entry.isDirectory()) return collectHtmlFiles(entryPath)
    return entry.name.endsWith('.html') ? [entryPath] : []
  })
}

function targetExists(urlPath) {
  const relativePath = urlPath.slice(pagesBase.length)
  if (!relativePath) return fs.existsSync(path.join(distDirectory, 'index.html'))

  const directTarget = path.join(distDirectory, relativePath)
  return fs.existsSync(directTarget) || fs.existsSync(path.join(directTarget, 'index.html'))
}

if (!fs.existsSync(distDirectory)) {
  console.error('GitHub Pages output check failed: dist directory does not exist.')
  process.exit(1)
}

const errors = []
for (const filePath of collectHtmlFiles(distDirectory)) {
  const html = fs.readFileSync(filePath, 'utf8')
  const relativeFile = path.relative(distDirectory, filePath)

  for (const match of html.matchAll(/\b(?:href|src)=["']([^"']+)["']/g)) {
    const url = match[1]
    if (!url.startsWith('/') || url.startsWith('//')) continue

    const urlPath = url.split(/[?#]/, 1)[0]
    if (!urlPath.startsWith(pagesBase)) {
      errors.push(`${relativeFile}: path escapes ${pagesBase}: ${url}`)
      continue
    }

    if (!targetExists(urlPath)) {
      errors.push(`${relativeFile}: target does not exist: ${url}`)
    }
  }
}

if (errors.length > 0) {
  console.error('GitHub Pages output check failed:')
  for (const error of errors) console.error(`- ${error}`)
  process.exit(1)
}

console.log(`GitHub Pages output check passed for ${pagesBase}`)
