import { test as setup } from '@playwright/test'

const USER = process.env.E2E_USER || 'admin_siege'
const PASS = process.env.E2E_PASSWORD || 'Admin@2025!'

setup('authentification siège', async ({ page }) => {
  await page.goto('/login')
  await page.locator('input[autocomplete="username"]').fill(USER)
  await page.locator('input[type="password"]').fill(PASS)
  await page.locator('button.login-btn').click()
  await page.waitForURL(/\/$|\/\?/, { timeout: 30_000 })
  await page.context().storageState({ path: '.auth/user.json' })
})
