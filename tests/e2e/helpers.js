import { expect } from '@playwright/test'

const isRender = /onrender\.com/i.test(
  process.env.E2E_BASE_URL || process.env.FRONTEND_URL || '',
)
const DEFAULT_TIMEOUT = isRender ? 90_000 : 30_000

export async function waitForDashboard(page) {
  await page.goto('/')
  await expect(page.locator('.loading, .page-title, .error-state')).toBeVisible({
    timeout: DEFAULT_TIMEOUT,
  })

  if (await page.locator('.loading').isVisible()) {
    await expect(page.locator('.loading')).toBeHidden({ timeout: DEFAULT_TIMEOUT })
  }

  await expect(page.locator('.page-title')).toContainText('Stocks', {
    timeout: DEFAULT_TIMEOUT,
  })
  await expect(
    page.locator('.data-table-wrap, .empty-state, .error-state'),
  ).toBeVisible({ timeout: DEFAULT_TIMEOUT })
}

export function lotRows(page) {
  return page.locator('.data-table tbody tr')
}

export async function getStatValue(page, label) {
  const card = page.locator('.stat-card').filter({ hasText: label })
  return card.locator('.stat-value').textContent()
}
