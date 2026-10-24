import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'

/**
 * Shared content and UI standards stage.
 *
 * The rule pack lives in the user's shared agent directory so that every
 * project inherits the same rules. A repository may also carry a copy for
 * machines that do not have it. When neither exists, the stage reports and
 * skips instead of failing the gate.
 *
 * Mode: report by default, so the stage measures without blocking. Set
 * CONTENT_STANDARDS_MODE=enforce once the baseline is clean enough to hold
 * the gate.
 */

const ROOT = resolve(import.meta.dirname, '..')

const CANDIDATE_BASES = [
  process.env.CONTENT_STANDARDS_HOME,
  join(homedir(), '.agents', 'skills', 'content-standards'),
  join(ROOT, '.agents', 'skills', 'content-standards'),
].filter(Boolean)

const checker = CANDIDATE_BASES.map((base) =>
  join(base, 'scripts', 'content_standards_check.py')
).find((candidate) => existsSync(candidate))

if (!checker) {
  console.log('shared content standards checker not found; stage skipped')
  process.exit(0)
}

const mode = process.env.CONTENT_STANDARDS_MODE ?? 'report'
const result = spawnSync(
  'python3',
  [checker, '--root', ROOT, '--mode', mode, '--format', 'json', '--max-findings', '0'],
  { encoding: 'utf-8' }
)

if (result.status !== 0 && result.status !== 1) {
  console.error(result.stderr?.trim() || `checker exited ${result.status}`)
  process.exit(result.status ?? 1)
}

let report
try {
  report = JSON.parse(result.stdout)
} catch {
  console.log(result.stdout?.trim() || 'content standards: no report')
  process.exit(0)
}

const counts = {}
for (const finding of report.findings ?? []) {
  counts[finding.rule] = (counts[finding.rule] ?? 0) + 1
}
const rules = Object.entries(counts)
  .sort((a, b) => b[1] - a[1])
  .map(([rule, count]) => `${rule} ${count}`)
  .join(', ')

console.log(
  `content standards (${mode}): ${report.count ?? 0} finding(s) in ${report.scanned ?? 0} file(s)` +
    (rules ? ` — ${rules}` : '')
)

if (mode === 'enforce' && (report.count ?? 0) > 0) {
  for (const finding of (report.findings ?? []).slice(0, 50)) {
    console.error(`${finding.path}:${finding.line}  ${finding.rule}  ${finding.message}`)
  }
  process.exit(1)
}

process.exit(0)
