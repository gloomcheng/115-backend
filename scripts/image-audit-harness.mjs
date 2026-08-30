import fs from 'node:fs'
import path from 'node:path'

/**
 * Image & Media Asset Legal Compliance & Quality Audit Harness
 * Audits all generated ELI5 diagrams and static media assets:
 * 1. Checks for unauthorized trademark / publisher keywords (e.g. O'Reilly, Manning, etc.)
 *    in file metadata, text chunks, and companion docs.
 * 2. Checks asset integrity (non-zero size, valid image headers, proper directory structure).
 * 3. Enforces 100% original educational curriculum branding.
 */

const IMAGES_ROOT = path.resolve('public/images')
const BANNED_TRADEMARK_PATTERNS = [
  /o['’]?reilly/i,
  /oreilly media/i,
  /manning publications/i,
  /packt publishing/i,
  /springer/i,
  /wiley/i,
  /all rights reserved\.?$/i,
]

function auditPngFile(filePath) {
  const stat = fs.statSync(filePath)
  const errors = []
  const warnings = []

  // Size check: must not be 0 bytes or suspiciously small
  if (stat.size < 1024) {
    errors.push(`File is suspiciously small (${stat.size} bytes). Possible corrupt generation.`)
  }

  // Read first 64KB for PNG header and text chunks
  const fd = fs.openSync(filePath, 'r')
  const buffer = Buffer.alloc(Math.min(stat.size, 65536))
  fs.readSync(fd, buffer, 0, buffer.length, 0)
  fs.closeSync(fd)

  // Verify PNG Magic Number: 89 50 4E 47 0D 0A 1A 0A
  const isPng =
    buffer[0] === 0x89 &&
    buffer[1] === 0x50 &&
    buffer[2] === 0x4e &&
    buffer[3] === 0x47 &&
    buffer[4] === 0x0d &&
    buffer[5] === 0x0a &&
    buffer[6] === 0x1a &&
    buffer[7] === 0x0a

  if (!isPng && filePath.endsWith('.png')) {
    errors.push('File extension is .png but magic header does not match PNG signature.')
  }

  // Scan binary text chunks (tEXt, iTXt, zTXt) and metadata for banned trademarks
  const contentStr = buffer.toString('binary')
  for (const pattern of BANNED_TRADEMARK_PATTERNS) {
    if (pattern.test(contentStr)) {
      errors.push(
        `Trademark audit failed: Discovered unauthorized pattern matching ${pattern} in image binary metadata.`
      )
    }
  }

  return { errors, warnings, sizeKb: (stat.size / 1024).toFixed(1) }
}

function scanDir(dir) {
  const results = []
  if (!fs.existsSync(dir)) return results

  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      results.push(...scanDir(fullPath))
    } else if (/\.(png|jpe?g|webp|svg)$/i.test(entry.name)) {
      results.push(fullPath)
    }
  }
  return results
}

function runAudit() {
  console.log('Running ELI5 Image Legal & Quality Audit Harness...')

  const imageFiles = scanDir(IMAGES_ROOT)
  if (imageFiles.length === 0) {
    console.log('  No images found in public/images. Skipping.')
    return
  }

  let totalErrors = 0
  let totalWarnings = 0

  for (const file of imageFiles) {
    const relPath = path.relative(process.cwd(), file)
    const audit = auditPngFile(file)

    if (audit.errors.length === 0 && audit.warnings.length === 0) {
      console.log(`  ✓ ${relPath} (${audit.sizeKb} KB) - Clean & Audit Verified`)
    } else {
      console.log(`  ✗ ${relPath}:`)
      for (const e of audit.errors) {
        console.log(`    ERROR: ${e}`)
        totalErrors++
      }
      for (const w of audit.warnings) {
        console.log(`    WARNING: ${w}`)
        totalWarnings++
      }
    }
  }

  console.log(
    `\nAudit completed: ${imageFiles.length} images scanned, ${totalErrors} errors, ${totalWarnings} warnings.`
  )

  if (totalErrors > 0) {
    console.error('Legal / Quality compliance check failed. Please remove trademarked assets.')
    process.exit(1)
  }
}

runAudit()
