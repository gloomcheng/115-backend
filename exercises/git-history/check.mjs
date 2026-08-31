#!/usr/bin/env node

import { execFileSync, spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

const repository = process.argv[2] ? resolve(process.argv[2]) : process.cwd()
const failures = []

function git(args) {
  return execFileSync('git', ['-C', repository, ...args], { encoding: 'utf8' }).trim()
}

function check(description, condition) {
  if (condition) console.log(`PASS: ${description}`)
  else {
    console.error(`FAIL: ${description}`)
    failures.push(description)
  }
}

function refExists(ref) {
  return spawnSync('git', ['-C', repository, 'rev-parse', '--verify', '--quiet', ref]).status === 0
}

function isAncestor(ancestor, descendant) {
  return (
    spawnSync('git', ['-C', repository, 'merge-base', '--is-ancestor', ancestor, descendant])
      .status === 0
  )
}

if (!existsSync(repository)) {
  console.error(`Repository path does not exist: ${repository}`)
  process.exit(1)
}

try {
  git(['rev-parse', '--is-inside-work-tree'])
} catch {
  console.error(`Not a Git working tree: ${repository}`)
  process.exit(1)
}

const requiredRefs = [
  'refs/heads/main',
  'refs/heads/feature/shipping',
  'refs/heads/copy/red',
  'refs/heads/hotfix/health',
  'refs/tags/lab/shipping-before-rebase',
  'refs/tags/lab/shipping-after-rebase',
]
for (const ref of requiredRefs) check(`Reference exists: ${ref}`, refExists(ref))

if (failures.length === 0) {
  const beforeRebase = git(['rev-parse', 'lab/shipping-before-rebase'])
  const afterRebase = git(['rev-parse', 'lab/shipping-after-rebase'])
  check('Rebase created a new shipping commit ID', beforeRebase !== afterRebase)
  check('Shipping history is included in main', isAncestor('feature/shipping', 'main'))
  check('Hotfix history is included in main', isAncestor('hotfix/health', 'main'))

  const snippetCommits = git(['log', '-S', '0.9', '--format=%H', '--', 'app.py'])
    .split('\n')
    .filter(Boolean)
  check('Discount snippet can be traced across at least three commits', snippetCommits.length >= 3)

  const currentApp = git(['show', 'main:app.py'])
  check('Main contains the restored discount snippet', currentApp.includes('price * 0.9'))
  check('Main contains the shipping calculation', currentApp.includes('price + shipping'))

  const mergeLine = git(['log', '--all', '--format=%H%x09%s'])
    .split('\n')
    .find((line) => line.endsWith('\tresolve checkout copy conflict'))
  check('Conflict resolution commit exists', Boolean(mergeLine))
  if (mergeLine) {
    const mergeCommit = mergeLine.split('\t')[0]
    const parents = git(['show', '-s', '--format=%P', mergeCommit]).split(/\s+/).filter(Boolean)
    check('Conflict resolution is a merge commit with two parents', parents.length === 2)
  }

  const message = git(['show', 'main:message.txt'])
  check('Conflict markers are absent from the resolved file', !/[<=>]{7}/.test(message))
  check('Resolved copy matches the chosen result', message === 'Checkout ready')
  check('Health checkpoint is present on main', git(['show', 'main:health.txt']) === 'ok')
}

const worktreePaths = git(['worktree', 'list', '--porcelain'])
  .split('\n')
  .filter((line) => line.startsWith('worktree '))
  .map((line) => line.slice('worktree '.length))
for (const worktreePath of worktreePaths) {
  const status = execFileSync('git', ['-C', worktreePath, 'status', '--porcelain'], {
    encoding: 'utf8',
  }).trim()
  check(`Worktree is clean: ${worktreePath}`, status === '')
}

if (failures.length > 0) process.exit(1)
console.log('Git history harness passed.')
