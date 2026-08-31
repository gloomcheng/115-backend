#!/usr/bin/env node

import { resolve4 } from 'node:dns/promises'
import { readFileSync } from 'node:fs'
import { connect } from 'node:net'
import { resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const API_DIR = resolve(ROOT, 'examples/http-api')

const files = {
  compose: readFileSync(resolve(API_DIR, 'compose.yaml'), 'utf8'),
  dockerfile: readFileSync(resolve(API_DIR, 'Dockerfile'), 'utf8'),
  nginx: readFileSync(resolve(API_DIR, 'deploy/nginx/backend-api.conf'), 'utf8'),
  tests: readFileSync(resolve(API_DIR, 'tests/test_main.py'), 'utf8'),
}

const checks = [
  ['Compose binds the application to loopback', files.compose.includes('127.0.0.1:8000:8000')],
  [
    'Compose does not publish bare port 8000',
    !/^\s*-\s*["']?8000:8000["']?\s*$/m.test(files.compose),
  ],
  ['Compose defines a restart policy', files.compose.includes('restart: unless-stopped')],
  ['Compose defines a health check', files.compose.includes('healthcheck:')],
  ['Compose defines an isolated test image', files.compose.includes('target: test')],
  [
    'Runtime image uses a non-root user',
    /FROM base AS runtime[\s\S]*\nUSER appuser\n/.test(files.dockerfile),
  ],
  ['Runtime image never uses the development server', !files.dockerfile.includes('fastapi dev')],
  [
    'FastAPI accepts proxy headers at the private boundary',
    files.dockerfile.includes('--proxy-headers'),
  ],
  [
    'Nginx proxies only to loopback port 8000',
    files.nginx.includes('proxy_pass http://127.0.0.1:8000;'),
  ],
  ['Nginx forwards the original host', files.nginx.includes('proxy_set_header Host $host;')],
  [
    'Nginx forwards the original scheme',
    files.nginx.includes('proxy_set_header X-Forwarded-Proto $scheme;'),
  ],
  ['API tests cover a successful health response', files.tests.includes('test_health_returns_200')],
  ['API tests cover a missing resource', files.tests.includes('test_missing_user_returns_404')],
]

function fail(message) {
  console.error(`FAIL: ${message}`)
  process.exitCode = 1
}

function parseOption(name) {
  const prefix = `--${name}=`
  const argument = process.argv.slice(2).find((value) => value.startsWith(prefix))
  return argument ? argument.slice(prefix.length) : null
}

async function expectPortClosed(host, port) {
  return new Promise((resolvePromise, rejectPromise) => {
    const socket = connect({ host, port })
    const timer = setTimeout(() => {
      socket.destroy()
      resolvePromise()
    }, 3000)

    socket.once('connect', () => {
      clearTimeout(timer)
      socket.destroy()
      rejectPromise(new Error(`Public port ${port} is reachable`))
    })
    socket.once('error', () => {
      clearTimeout(timer)
      resolvePromise()
    })
  })
}

async function fetchWithTimeout(url, options = {}) {
  return fetch(url, { ...options, signal: AbortSignal.timeout(8000) })
}

async function liveChecks(baseUrl, expectedIp) {
  const base = new URL(baseUrl)
  if (base.protocol !== 'https:') throw new Error('--url must start with https://')
  if (base.pathname !== '/' || base.search || base.hash) {
    throw new Error('--url must contain only the public origin, without a path or query')
  }

  const addresses = await resolve4(base.hostname)
  if (expectedIp && !addresses.includes(expectedIp)) {
    throw new Error(`DNS returned ${addresses.join(', ')}, expected ${expectedIp}`)
  }

  await expectPortClosed(base.hostname, 8000)

  const httpHealth = new URL('/health', base)
  httpHealth.protocol = 'http:'
  const redirect = await fetchWithTimeout(httpHealth, { redirect: 'manual' })
  if (![301, 302, 307, 308].includes(redirect.status)) {
    throw new Error(`HTTP did not redirect to HTTPS; received ${redirect.status}`)
  }
  const location = redirect.headers.get('location')
  if (!location || new URL(location, httpHealth).protocol !== 'https:') {
    throw new Error('HTTP redirect Location is not an HTTPS URL')
  }

  const health = await fetchWithTimeout(new URL('/health', base))
  const healthBody = await health.json()
  if (health.status !== 200 || healthBody.ok !== true) {
    throw new Error(`HTTPS health check failed with status ${health.status}`)
  }

  const requestInfo = await fetchWithTimeout(new URL('/request-info', base))
  const requestBody = await requestInfo.json()
  if (
    requestInfo.status !== 200 ||
    requestBody.scheme !== 'https' ||
    requestBody.host !== base.host
  ) {
    throw new Error('Forwarded request information does not match the public HTTPS origin')
  }

  console.log(
    `Live deployment passed: ${base.origin} resolves, redirects, serves HTTPS, and keeps port 8000 private.`
  )
}

for (const [description, passed] of checks) {
  if (passed) console.log(`PASS: ${description}`)
  else fail(description)
}

if (process.exitCode) process.exit(process.exitCode)

const liveUrl = parseOption('url')
const expectedIp = parseOption('expected-ip')
if (liveUrl) {
  await liveChecks(liveUrl, expectedIp).catch((error) => fail(error.message))
} else {
  console.log(
    'Static deployment contract passed. Add --url=https://host --expected-ip=address for live checks.'
  )
}
