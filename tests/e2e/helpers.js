import { expect } from '@playwright/test'

export async function waitForDashboard(page) {
  await page.goto('/')
  await expect(page.locator('.page-title')).toContainText('Stocks', { timeout: 30_000 })
  await expect(page.locator('.ag-root-wrapper')).toBeVisible({ timeout: 30_000 })
}

export async function getStatValue(page, label) {
  const card = page.locator('.stat-card').filter({ hasText: label })
  return card.locator('.stat-value').textContent()
}
