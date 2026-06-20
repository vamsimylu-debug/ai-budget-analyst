import { test, expect } from '@playwright/test'

test('group high-risk by department', async ({ page, request }) => {
  const appBase = process.env.APP_URL || 'http://localhost:3000'
  // enable test mode so frontend uses non-streaming JSON endpoint
  await page.addInitScript(() => {
    window.__TEST_MODE__ = true
    // record which transport is used
    window._TEST_LOGS = []
    const origFetch = window.fetch.bind(window)
    window.fetch = (...args) => {
      window._TEST_LOGS.push(['fetch', args[0]])
      return origFetch(...args)
    }
    const OrigEventSource = window.EventSource
    // wrap EventSource to record usage
    // eslint-disable-next-line no-global-assign
    window.EventSource = function(url) {
      window._TEST_LOGS.push(['EventSource', url])
      return new OrigEventSource(url)
    }
  })
  await page.goto(`${appBase}/?test=1`)
  // debug: confirm test flag is set in page context
  const testFlag = await page.evaluate(() => (window as any).__TEST_MODE__)
  console.log('TEST_FLAG:', testFlag)
  // log console messages for debugging
  page.on('console', msg => console.log('PAGE LOG:', msg.text()))
  // log network requests for debugging
  page.on('request', req => {
    if (req.url().includes('/api/scenarios/')) console.log('REQ:', req.method(), req.url())
  })
  page.on('requestfailed', req => {
    if (req.url().includes('/api/scenarios/')) console.log('REQ FAILED:', req.failure(), req.url())
  })
  page.on('response', async res => {
    if (res.url().includes('/api/scenarios/1/chat')) {
      const text = await res.text().catch(() => '<no body>')
      console.log('CHAT_RESPONSE:', res.status(), text)
    }
  })
  await page.waitForSelector('.scenario-list button')
  // prefer selecting the seeded scenario by name, otherwise select the first
  const seeded = page.locator('.scenario-list button', { hasText: 'Q2 Operational Budget' })
  if (await seeded.count() > 0) {
    await seeded.first().click()
  } else {
    await page.click('.scenario-list button')
  }

  const runtimeInfo = await page.evaluate(() => ({
    readyState: document.readyState,
    testMode: window.__TEST_MODE__,
    testQuery: new URL(window.location.href).searchParams.get('test'),
    injectorType: typeof window.__playwright_inject,
  }))
  console.log('RUNTIME_INFO:', runtimeInfo)

  // ensure the chat panel is mounted and ready to receive injected events
  await page.waitForSelector('.chat-window', { timeout: 10000 })
  const runtimeInfo2 = await page.evaluate(() => ({
    readyState: document.readyState,
    testMode: window.__TEST_MODE__,
    injectorType: typeof window.__playwright_inject,
    logs: Array.isArray(window._TEST_LOGS) ? window._TEST_LOGS : null,
  }))
  console.log('RUNTIME_INFO_AFTER_CHAT_PANEL:', runtimeInfo2)

  const question = 'Paid Ads Travel 15000 7500 High Medium Group this by department and show only high-risk items'
  await page.fill('input[placeholder="Ask about budget variances, risk, or scenarios"]', question)
  await page.click('.chat-input-row button')

  // wait for test-mode JSON response to render in the chat window
  await page.waitForFunction(() => {
    const w = document.querySelector('.chat-window')
    if (!w) return false
    const text = w.textContent || ''
    if (text.includes('Marketing')) return true
    if (w.querySelector('.result-card')) return true
    return false
  }, null, { timeout: 30000 })

  const chatText = await page.locator('.chat-window').innerText()
  expect(chatText).toContain('Marketing')
  expect(chatText).toMatch(/Found \d+ line items grouped by department/i)
})
