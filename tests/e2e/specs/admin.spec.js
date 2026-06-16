import { test, expect } from '@playwright/test'

test('page utilisateurs reservee a l admin', async ({ page }) => {
  await page.goto('/users')
  await expect(page.locator('.page-title')).toContainText('Gestion des utilisateurs', { timeout: 20_000 })
  await expect(page.locator('.users-row').first()).toBeVisible({ timeout: 15_000 })
  await expect(page.locator('.users-username').first()).not.toBeEmpty()
})
