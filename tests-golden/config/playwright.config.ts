// 🔒 黄金测试 Playwright 配置
// 此文件受保护，仅允许人工修改

import { defineConfig, devices } from "@playwright/test";

/**
 * 黄金测试配置 - 核心业务逻辑测试
 * 这些测试不允许AI修改，确保代码质量的权威性
 */
export default defineConfig({
  // 测试目录
  testDir: "../e2e",

  // 全局设置
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // 报告配置
  reporter: [
    ["html", { outputFolder: "../reports/golden-playwright-report" }],
    ["json", { outputFile: "../reports/golden-test-results.json" }],
    ["junit", { outputFile: "../reports/golden-junit-results.xml" }],
  ],

  // 全局配置
  use: {
    baseURL: process.env.TEST_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",

    // 黄金测试专用标识
    extraHTTPHeaders: {
      "X-Test-Type": "golden",
    },
  },

  // 项目配置
  projects: [
    {
      name: "golden-chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "golden-firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "golden-webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],

  // Web服务器配置（如果需要）
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // 超时设置
  timeout: 30 * 1000,
  expect: {
    timeout: 5 * 1000,
  },

  // 输出目录
  outputDir: "../reports/golden-test-results/",
});
