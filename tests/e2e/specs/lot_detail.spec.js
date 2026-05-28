import { test, expect } from '@playwright/test'

test('page détail lot affiche les courbes', async ({ page }) => {
  await page.goto('/lots/demo-lot-001')
  await expect(page.locator('.page-title')).toContainText('Détail du lot')
})
