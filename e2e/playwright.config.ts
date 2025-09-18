// Playwright配置修复 - 针对CI环境优化
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined, // CI环境使用单worker避免冲突

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }],
    ['line'],
  ],

  use: {
    baseURL: process.env.TEST_BASE_URL || process.env.FRONTEND_URL || 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    navigationTimeout: 30 * 1000,
    actionTimeout: 10 * 1000,
    ignoreHTTPSErrors: true,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 优化的webServer配置 - 修复CI环境路径问题
  webServer: process.env.CI
    ? undefined
    : {
        command: 'npm run preview -- --port 3001 --host 0.0.0.0',
        cwd: '../frontend',
        port: 3001,
        reuseExistingServer: true,
        timeout: 120 * 1000,
        env: {
          NODE_ENV: 'production',
          VITE_API_URL: 'http://localhost:8000',
        },
      },
});
