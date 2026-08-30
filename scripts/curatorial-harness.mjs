import fs from 'node:fs'
import path from 'node:path'

const requiredPages = [
  'src/pages/index.astro',
  'src/pages/book.astro',
  'src/pages/glossary.astro',
  'src/pages/preparation.astro',
  'src/pages/lessons/[slug].astro',
]

const layoutSources = ['src/layouts/Layout.astro', ...requiredPages]

const failures = []

const globalCssPath = path.resolve('src/styles/global.css')
const globalCss = fs.readFileSync(globalCssPath, 'utf8')
const themeStart = globalCss.indexOf('@theme')
let cssWithoutTheme = globalCss
if (themeStart >= 0) {
  const openingBrace = globalCss.indexOf('{', themeStart)
  let depth = 0
  let themeEnd = openingBrace
  for (let index = openingBrace; index < globalCss.length; index += 1) {
    if (globalCss[index] === '{') depth += 1
    if (globalCss[index] === '}') depth -= 1
    if (depth === 0) {
      themeEnd = index + 1
      break
    }
  }
  cssWithoutTheme = `${globalCss.slice(0, themeStart)}${globalCss.slice(themeEnd)}`
}
const unsupportedCss = cssWithoutTheme
  .replace(/@import\s+[^;]+;/g, '')
  .replace(/@plugin\s+[^;]+;/g, '')
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .trim()
if (unsupportedCss.length > 0) {
  failures.push('src/styles/global.css contains custom CSS. Use Tailwind utilities in components.')
}

for (const file of layoutSources) {
  const content = fs.readFileSync(path.resolve(file), 'utf8')
  const visibleSource = content.replace(/<!--[\s\S]*?-->/g, '')
  if (/[\u4e00-\u9fff]/.test(visibleSource)) {
    failures.push(
      `${file} contains course copy. Move it to src/data or src/content before changing layout.`
    )
  }
}

if (failures.length > 0) {
  console.error('Curatorial system check failed:')
  failures.forEach((failure) => {
    console.error(`- ${failure}`)
  })
  process.exit(1)
}

console.log('Curatorial system check passed.')
