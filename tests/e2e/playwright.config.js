import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './specs',
  use: {
    baseURL: 'http://localhost:80',
  },
  reporter: [['junit', { outputFile: '../reports/e2e-results.xml' }]],
})
