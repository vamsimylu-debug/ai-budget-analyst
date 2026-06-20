import { test, expect } from '@playwright/test'

test('backend SSE grouping returns high-risk table', async ({ request }) => {
  const backendBase = process.env.BACKEND_URL || 'http://127.0.0.1:8000'
  const q = encodeURIComponent('Paid Ads Travel 15000 7500 High Medium Group this by department and show only high-risk items')
  const res = await request.get(`${backendBase}/api/scenarios/1/chat/?question=${q}`)
  expect(res.status()).toBe(200)
  const body = await res.text()
  expect(body).toContain('event: table')
  expect(body).toContain('Marketing')
})
