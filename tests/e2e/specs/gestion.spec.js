import { test, expect } from '@playwright/test'

test('onglet lots visible pour admin pays', async ({ page }) => {
  await page.goto('/gestion/lots')
  await expect(page.locator('.page-title')).toContainText('Gestion des lots', { timeout: 20_000 })
})

test('onglet entrepots visible pour admin pays', async ({ page }) => {
  await page.goto('/gestion/entrepots')
  await expect(page.locator('.page-title')).toContainText('Gestion des entrepôts', { timeout: 20_000 })
})

test('referentiels reserve au super admin', async ({ page }) => {
  await page.goto('/gestion/referentiels')
  await expect(page.locator('.page-title')).toContainText('Référentiels', { timeout: 20_000 })
  await expect(page.locator('.gestion-tab')).toHaveCount(2)
})
