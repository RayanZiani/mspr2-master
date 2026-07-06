import { test as setup } from '@playwright/test'

const USER = process.env.E2E_USER || 'admin_siege'
const PASS = process.env.E2E_PASSWORD || 'Admin@2025!'
const isRender = /onrender\.com/i.test(
  process.env.E2E_BASE_URL || process.env.FRONTEND_URL || '',
)
const MAX_ATTEMPTS = isRender ? 6 : 2
const RETRY_DELAY_MS = isRender ? 8_000 : 2_000

setup('authentification siège', async ({ page }) => {
  let lastError

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      await page.goto('/login', { waitUntil: 'domcontentloaded', timeout: 60_000 })
      await page.locator('input[autocomplete="username"]').fill(USER)
      await page.locator('input[type="password"]').fill(PASS)
      await page.locator('button.login-btn').click()
      await page.waitForURL(/\/$|\/\?/, { timeout: 45_000 })
      await page.context().storageState({ path: '.auth/user.json' })
      return
    } catch (error) {
      lastError = error
      if (attempt < MAX_ATTEMPTS) {
        await page.waitForTimeout(RETRY_DELAY_MS)
      }
    }
  }

  throw lastError
})
