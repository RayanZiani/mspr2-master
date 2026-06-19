import { test, expect } from '@playwright/test'

test.use({ storageState: { cookies: [], origins: [] } })

test('redirection vers login si non authentifié', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL(/\/login/, { timeout: 15_000 })
  await expect(page.locator('button.login-btn')).toBeVisible()
})

test('login échoue avec mauvais mot de passe', async ({ page }) => {
  await page.goto('/login')
  await page.locator('input[autocomplete="username"]').fill('admin_siege')
  await page.locator('input[type="password"]').fill('wrong-password')
  await page.locator('button.login-btn').click()
  await expect(page).toHaveURL(/\/login/)
})
