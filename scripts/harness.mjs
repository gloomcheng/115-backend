import { spawnSync } from 'node:child_process'

/**
 * 115-backend Unified Harness Framework
 * Consolidates all editorial, code quality, accessibility, CJK typography,
 * typecheck, and build validation pipelines into a single high-performance runner.
 */

const args = process.argv.slice(2)
const isFix = args.includes('--fix') || args.includes('-f')
const isFast = args.includes('--fast')

const STAGES = [
  {
    name: 'Biome Linter & Formatter',
    cmd: isFix ? 'npx' : 'npx',
    args: isFix ? ['biome', 'check', '--write', '.'] : ['biome', 'check', '.'],
  },
  {
    name: 'English Code & Comment Guard',
    cmd: 'node',
    args: ['scripts/english-code-check.mjs'],
  },
  {
    name: 'CJK Spacing Typography Guard',
    cmd: 'node',
    args: ['scripts/cjk-spacing-check.mjs'],
  },
  {
    name: 'Emoji & Icon Set Guard',
    cmd: 'node',
    args: ['scripts/emoji-icon-harness.mjs'],
  },
  {
    name: 'Curatorial System Guard',
    cmd: 'node',
    args: ['scripts/curatorial-harness.mjs'],
  },
  {
    name: 'Reference Library Guard',
    cmd: 'node',
    args: ['scripts/reference-library-harness.mjs'],
  },
  {
    name: "O'Reilly Editorial Review Guard",
    cmd: 'node',
    args: ['scripts/oreilly-review-harness.mjs'],
  },
  {
    name: 'Image Legal & Quality Audit Guard',
    cmd: 'node',
    args: ['scripts/image-audit-harness.mjs'],
  },
  {
    name: 'Astro TypeScript Typecheck',
    cmd: 'npx',
    args: ['astro', 'check'],
  },
  {
    name: 'Astro Static Monograph Build',
    cmd: 'npx',
    args: ['astro', 'build'],
  },
  {
    name: 'Accessibility (A11y) & Font Size Guard',
    cmd: 'node',
    args: ['scripts/a11y-check.mjs'],
  },
]

function runHarness() {
  const startTime = Date.now()
  console.log('\n=================================================================')
  console.log('       115-BACKEND UNIFIED EDITORIAL & CODE HARNESS')
  console.log('=================================================================\n')

  let failedCount = 0
  const results = []

  for (let i = 0; i < STAGES.length; i++) {
    const stage = STAGES[i]
    if (isFast && (stage.name.includes('Build') || stage.name.includes('Accessibility'))) {
      continue
    }

    const stageStart = Date.now()
    process.stdout.write(`[${i + 1}/${STAGES.length}] Running ${stage.name}... `)

    const result = spawnSync(stage.cmd, stage.args, {
      stdio: 'pipe',
      encoding: 'utf-8',
    })

    const duration = ((Date.now() - stageStart) / 1000).toFixed(2)

    if (result.status === 0) {
      console.log(`\x1b[32mPASSED\x1b[0m (${duration}s)`)
      results.push({ name: stage.name, status: 'PASSED', duration })
    } else {
      console.log(`\x1b[31mFAILED\x1b[0m (${duration}s)`)
      if (result.stdout) console.log(result.stdout)
      if (result.stderr) console.error(result.stderr)
      results.push({ name: stage.name, status: 'FAILED', duration })
      failedCount++
      break
    }
  }

  const totalDuration = ((Date.now() - startTime) / 1000).toFixed(2)
  console.log('\n-----------------------------------------------------------------')
  if (failedCount === 0) {
    console.log(
      `\x1b[32m✓ ALL CHECKS PASSED\x1b[0m in ${totalDuration}s. Ready for publishing & peer review.`
    )
    console.log('-----------------------------------------------------------------\n')
    process.exit(0)
  } else {
    console.log(
      `\x1b[31m✗ HARNESS FAILED\x1b[0m in ${totalDuration}s. Please resolve issues above.`
    )
    console.log('-----------------------------------------------------------------\n')
    process.exit(1)
  }
}

runHarness()
