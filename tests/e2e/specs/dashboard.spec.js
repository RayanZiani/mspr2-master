import { test, expect } from '@playwright/test'

test('dashboard charge et affiche les lots', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('FutureKawa')
  await expect(page.locator('.ag-root')).toBeVisible()
})
