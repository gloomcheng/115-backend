#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { basename, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(import.meta.dirname, '..')
const MAX_TEXT_BYTES = 1024 * 1024

const forbiddenPathRules = [
  {
    id: 'environment-file',
    test: (path) => /(^|\/)\.env(?:\.|$)/.test(path) && !path.endsWith('.env.example'),
  },
  {
    id: 'private-key-file',
    test: (path) => /\.(?:key|pem|p12|pfx|jks)$/i.test(path),
  },
  {
    id: 'ssh-private-key',
    test: (path) => /(^|\/)(?:id_rsa|id_dsa|id_ecdsa|id_ed25519)$/.test(path),
  },
  {
    id: 'credential-bundle',
    test: (path) =>
      /(^|\/)(?:credentials|service[-_]?account|client[-_]?secret)s?\.json$/i.test(path),
  },
]

const contentRules = [
  {
    id: 'private-key-content',
    regex: /-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/i,
  },
  {
    id: 'aws-access-key',
    regex: /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/,
  },
  {
    id: 'github-token',
    regex: /\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{30,})\b/,
  },
  {
    id: 'slack-token',
    regex: /\bxox[baprs]-[A-Za-z0-9-]{20,}\b/,
  },
  {
    id: 'credential-in-url',
    regex: /\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?):\/\/[^:\s/]+:[^@\s/]+@/i,
  },
]

const literalAssignment =
  /(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*["']([^"'\n]{8,})["']/gi
const safeLiteral =
  /^(?:example|fake|dummy|test(?:-only)?|change-?me|not-a-secret|redacted|placeholder)/i

export function pathPolicyFindings(path) {
  return forbiddenPathRules
    .filter((rule) => rule.test(path))
    .map((rule) => ({ path, line: null, rule: rule.id }))
}

export function contentPolicyFindings(path, content) {
  const findings = []
  const lines = content.split('\n')

  for (let index = 0; index < lines.length; index++) {
    const line = lines[index]
    for (const rule of contentRules) {
      rule.regex.lastIndex = 0
      if (rule.regex.test(line)) {
        findings.push({ path, line: index + 1, rule: rule.id })
      }
    }

    literalAssignment.lastIndex = 0
    let match = literalAssignment.exec(line)
    while (match) {
      if (!safeLiteral.test(match[1])) {
        findings.push({ path, line: index + 1, rule: 'hardcoded-secret-literal' })
      }
      match = literalAssignment.exec(line)
    }
  }

  if (basename(path) === '.env.example') {
    for (let index = 0; index < lines.length; index++) {
      const line = lines[index].trim()
      if (!line || line.startsWith('#') || !line.includes('=')) continue
      const key = line.slice(0, line.indexOf('=')).trim()
      const value = line
        .slice(line.indexOf('=') + 1)
        .trim()
        .replace(/^['"]|['"]$/g, '')
      const sensitiveKey =
        /(?:password|passwd|pwd|secret|api[_-]?key|token|private[_-]?key|database_url)/i.test(key)
      if (sensitiveKey && value && !safeLiteral.test(value) && !/^\$\{[^}]+\}$/.test(value)) {
        findings.push({ path, line: index + 1, rule: 'env-example-has-value' })
      }
    }
  }

  return findings
}

function gitLines(args) {
  const output = execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' })
  return output
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function stagedContent(path) {
  return execFileSync('git', ['show', `:${path}`], {
    cwd: ROOT,
    encoding: 'utf8',
    maxBuffer: MAX_TEXT_BYTES * 2,
  })
}

function workingContent(path) {
  const absolutePath = resolve(ROOT, path)
  if (!existsSync(absolutePath) || statSync(absolutePath).size > MAX_TEXT_BYTES) return null
  const buffer = readFileSync(absolutePath)
  if (buffer.includes(0)) return null
  return buffer.toString('utf8')
}

function main() {
  const mode = process.argv.includes('--staged') ? 'staged' : 'all'
  const files =
    mode === 'staged'
      ? gitLines(['diff', '--cached', '--name-only', '--diff-filter=ACMR'])
      : gitLines(['ls-files', '--cached', '--others', '--exclude-standard'])
  const findings = []

  for (const path of files) {
    findings.push(...pathPolicyFindings(path))
    let content = null
    try {
      content = mode === 'staged' ? stagedContent(path) : workingContent(path)
    } catch {
      continue
    }
    if (content !== null) findings.push(...contentPolicyFindings(path, content))
  }

  if (findings.length > 0) {
    console.error('Secret policy failed. Potential values are redacted by design.')
    for (const finding of findings) {
      const location = finding.line ? `${finding.path}:${finding.line}` : finding.path
      console.error(`  ${location} [${finding.rule}]`)
    }
    console.error('Remove the value from the staged file. If it was real, revoke and rotate it.')
    process.exit(1)
  }

  console.log(
    `Secret policy passed: ${files.length} ${mode === 'staged' ? 'staged' : 'working'} files checked.`
  )
}

const isDirectRun = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)
if (isDirectRun) main()
