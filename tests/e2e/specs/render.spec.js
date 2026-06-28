import { test, expect } from '@playwright/test'
import { waitForDashboard, lotRows } from '../helpers.js'

const COUNTRY_FILTERS = ['Brésil', 'Équateur', 'Colombie']

test('page configuration capteurs accessible pour admin', async ({ page }) => {
  await page.goto('/config/capteurs')
  await expect(page.locator('.page-title')).toContainText('Configuration capteurs', {
    timeout: 30_000,
  })
  await expect(page.locator('.card, form, table').first()).toBeVisible({ timeout: 20_000 })
})

test('dashboard filtre chaque pays', async ({ page }) => {
  await waitForDashboard(page)
  const totalBefore = await lotRows(page).count()

  for (const country of COUNTRY_FILTERS) {
    await page.getByRole('button', { name: country }).click()
    await expect(page.getByRole('button', { name: country })).toHaveClass(/active/)
    const totalAfter = await lotRows(page).count()
    expect(totalAfter).toBeLessThanOrEqual(totalBefore)
  }
})

test('page alertes sans erreur API', async ({ page }) => {
  await page.goto('/alertes')
  await expect(page.locator('.page-title')).toContainText('Alertes actives', { timeout: 30_000 })
  await expect(page.locator('.error-state')).toHaveCount(0)
  await expect(page.locator('.data-table-wrap, .empty-state, .card').first()).toBeVisible({
    timeout: 20_000,
  })
})

test('page mesures affiche le selecteur de lot', async ({ page }) => {
  await page.goto('/mesures')
  await expect(page.locator('.page-title')).toContainText('Mesures', { timeout: 30_000 })
  await expect(page.locator('#lot-select, select').first()).toBeVisible({ timeout: 20_000 })
})
