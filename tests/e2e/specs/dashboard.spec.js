import { test, expect } from '@playwright/test'
import { waitForDashboard, getStatValue, lotRows } from '../helpers.js'

test('dashboard charge et affiche les lots', async ({ page }) => {
  await waitForDashboard(page)
  await expect(page.locator('.stat-card')).toHaveCount(4)
  const total = await getStatValue(page, 'Total lots')
  expect(Number(total)).toBeGreaterThanOrEqual(0)
  await expect(page.locator('.sync-info')).toContainText('Derniere synchro')
})

test('filtre pays Brésil réduit la grille', async ({ page }) => {
  await waitForDashboard(page)
  const totalBefore = await lotRows(page).count()
  await page.getByRole('button', { name: 'Brésil' }).click()
  await expect(page.getByRole('button', { name: 'Brésil' })).toHaveClass(/active/)
  const totalAfter = await lotRows(page).count()
  expect(totalAfter).toBeLessThanOrEqual(totalBefore)
})

test('recherche lot par texte', async ({ page }) => {
  await waitForDashboard(page)
  await page.locator('input.input').fill('lot')
  await expect(page.locator('.data-table-wrap, .empty-state')).toBeVisible()
})

test('filtre statut conforme', async ({ page }) => {
  await waitForDashboard(page)
  await page.getByLabel('Conforme').check()
  await expect(page.locator('.data-table-wrap, .empty-state')).toBeVisible()
})
