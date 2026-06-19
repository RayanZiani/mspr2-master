import { test, expect } from '@playwright/test'
import { waitForDashboard, lotRows } from '../helpers.js'

test('page détail lot affiche les courbes', async ({ page }) => {
  await waitForDashboard(page)

  const firstRow = lotRows(page).first()
  if (!(await firstRow.count())) {
    test.skip(true, 'Aucun lot en base — seed requis')
  }

  await firstRow.click()
  await expect(page).toHaveURL(/\/lots\//)
  await expect(page.locator('.page-title')).toContainText('Détail du lot', { timeout: 15_000 })
  await expect(page.locator('.recharts-responsive-container, .card').first()).toBeVisible({ timeout: 15_000 })
})

test('retour dashboard depuis détail lot', async ({ page }) => {
  await waitForDashboard(page)
  const firstRow = lotRows(page).first()
  if (!(await firstRow.count())) {
    test.skip(true, 'Aucun lot en base')
  }

  await firstRow.click()
  await expect(page).toHaveURL(/\/lots\//)
  await page.getByRole('link', { name: 'Dashboard' }).click()
  await expect(page.locator('.page-title')).toContainText('Stocks')
})
