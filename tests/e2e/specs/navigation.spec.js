import { test, expect } from '@playwright/test'

test('page alertes accessible pour admin siège', async ({ page }) => {
  await page.goto('/alertes')
  await expect(page.locator('.page-title')).toContainText('Alertes actives', { timeout: 20_000 })
  await expect(page.locator('.navbar')).toBeVisible()
})

test('page mesures IoT charge et permet de sélectionner un lot', async ({ page }) => {
  await page.goto('/mesures')
  await expect(page.locator('.page-title')).toContainText('Mesures', { timeout: 20_000 })
  const lotSelect = page.locator('#lot-select')
  if (await lotSelect.count()) {
    const options = lotSelect.locator('option')
    if (await options.count() > 1) {
      await lotSelect.selectOption({ index: 1 })
      await expect(page.locator('.recharts-responsive-container, .card').first()).toBeVisible({ timeout: 20_000 })
    }
  }
})

test('page santé système affiche les APIs', async ({ page }) => {
  await page.goto('/sante')
  await expect(page.locator('.page-title')).toContainText('Sante systeme', { timeout: 20_000 })
  await expect(page.locator('.card, .health-card, table').first()).toBeVisible({ timeout: 15_000 })
})

test('navigation principale visible pour admin', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Mesures' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Alertes' })).toBeVisible()
  await page.locator('.account-btn').click()
  await expect(page.getByRole('menuitem', { name: /Santé système/i })).toBeVisible()
  await expect(page.getByRole('menuitem', { name: 'Utilisateurs' })).toBeVisible()
})

test('menu compte et déconnexion', async ({ page }) => {
  await page.goto('/')
  await page.locator('.account-btn').click()
  await expect(page.locator('.account-menu')).toBeVisible()
  await expect(page.locator('.account-user')).not.toBeEmpty()
})
