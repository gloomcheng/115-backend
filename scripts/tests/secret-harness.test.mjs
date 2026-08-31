import assert from 'node:assert/strict'
import test from 'node:test'

import { contentPolicyFindings, pathPolicyFindings } from '../secret-harness.mjs'

test('rejects environment files but allows the empty example', () => {
  assert.equal(pathPolicyFindings('service/.env.production').length, 1)
  assert.equal(pathPolicyFindings('service/.env.example').length, 0)
  assert.equal(contentPolicyFindings('.env.example', 'APP_SECRET=\n').length, 0)
})

test('rejects a private key marker without storing one in this test', () => {
  const marker = ['-----BEGIN ', 'PRIVATE KEY-----'].join('')

  assert.equal(contentPolicyFindings('config.txt', marker).length, 1)
})

test('rejects a hardcoded password and allows an environment lookup', () => {
  const unsafe = ['password = "', 'r3al-value-for-a-test', '"'].join('')
  const safe = 'password = os.environ["DATABASE_PASSWORD"]'

  assert.equal(contentPolicyFindings('settings.py', unsafe).length, 1)
  assert.equal(contentPolicyFindings('settings.py', safe).length, 0)
})

test('rejects credential-bearing database URLs', () => {
  const unsafe = ['postgresql://reader:', 'r3al-value-for-a-test', '@db.internal/app'].join('')

  assert.equal(contentPolicyFindings('settings.py', unsafe).length, 1)
})
