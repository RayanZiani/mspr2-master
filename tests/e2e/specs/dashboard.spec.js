import { test, expect } from '@playwright/test'

test('dashboard charge et affiche les lots', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.page-title')).toContainText('Stocks')
  await expect(page.locator('.ag-root')).toBeVisible()
})
