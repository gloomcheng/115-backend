#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const VERSION = '8.30.1'
const RELEASE_BASE = `https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}`
const CACHE_DIR = join(ROOT, '.cache', 'gitleaks', VERSION)

const artifacts = {
  'darwin-arm64': {
    file: `gitleaks_${VERSION}_darwin_arm64.tar.gz`,
    sha256: 'b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5',
  },
  'darwin-x64': {
    file: `gitleaks_${VERSION}_darwin_x64.tar.gz`,
    sha256: 'dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709',
  },
  'linux-arm64': {
    file: `gitleaks_${VERSION}_linux_arm64.tar.gz`,
    sha256: 'e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080',
  },
  'linux-x64': {
    file: `gitleaks_${VERSION}_linux_x64.tar.gz`,
    sha256: '551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb',
  },
  'win32-arm64': {
    file: `gitleaks_${VERSION}_windows_arm64.zip`,
    sha256: 'b95f5e4f5c425cedca7ee203d9afd29597e692c4924a12ed42f970537c72cc0f',
  },
  'win32-x64': {
    file: `gitleaks_${VERSION}_windows_x64.zip`,
    sha256: 'd29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e',
  },
}

async function downloadBinary() {
  const key = `${process.platform}-${process.arch}`
  const artifact = artifacts[key]
  if (!artifact) throw new Error(`Unsupported platform for Gitleaks: ${key}`)

  const binaryName = process.platform === 'win32' ? 'gitleaks.exe' : 'gitleaks'
  const binaryPath = join(CACHE_DIR, binaryName)
  if (existsSync(binaryPath)) return binaryPath

  mkdirSync(CACHE_DIR, { recursive: true })
  const archivePath = join(CACHE_DIR, artifact.file)
  const response = await fetch(`${RELEASE_BASE}/${artifact.file}`)
  if (!response.ok) throw new Error(`Gitleaks download failed with HTTP ${response.status}`)
  const archive = Buffer.from(await response.arrayBuffer())
  const actualHash = createHash('sha256').update(archive).digest('hex')
  if (actualHash !== artifact.sha256) throw new Error('Gitleaks checksum verification failed')

  writeFileSync(archivePath, archive)
  execFileSync('tar', ['-xf', archivePath, '-C', CACHE_DIR], { stdio: 'inherit' })
  rmSync(archivePath)
  if (process.platform !== 'win32') chmodSync(binaryPath, 0o755)
  return binaryPath
}

async function main() {
  const mode = process.argv[2] === 'staged' ? 'staged' : 'repo'
  const binaryPath = await downloadBinary()
  const args =
    mode === 'staged'
      ? ['git', '--staged', '--redact', '--no-banner', '.']
      : ['git', '--redact', '--no-banner', '.']

  execFileSync(binaryPath, args, { cwd: ROOT, stdio: 'inherit' })
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
