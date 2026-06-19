import { defineConfig, devices } from '@playwright/test'

const isCI = Boolean(process.env.CI || process.env.JENKINS_URL)

export default defineConfig({
  fullyParallel: false,
  retries: 1,
  workers: 1,
  timeout: 120_000,
  use: {
    baseURL: process.env.E2E_BASE_URL || process.env.FRONTEND_URL || 'http://localhost:80',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    launchOptions: isCI
      ? { args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] }
      : undefined,
  },
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.js/,
    },
    {
      name: 'chromium',
      testDir: './specs',
      testIgnore: /guest\.spec\.js/,
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'guest',
      testMatch: /guest\.spec\.js/,
      use: {
        ...devices['Desktop Chrome'],
        storageState: { cookies: [], origins: [] },
      },
    },
  ],
  reporter: [
    ['list'],
    ['junit', { outputFile: '../reports/e2e-results.xml' }],
    ['allure-playwright', { outputFolder: '../reports/allure-results' }],
  ],
})
