import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // 测试目录
  testDir: './tests',

  // 全局测试超时时间（30秒）
  timeout: 30 * 1000,

  // 每个测试的期望超时时间（5秒）
  expect: {
    timeout: 5000,
  },

  // 失败时重试次数
  retries: process.env.CI ? 2 : 0,

  // 并行执行的worker数量
  workers: process.env.CI ? 1 : undefined,

  // 测试报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }],
    ['line'],
  ],

  // 全局设置
  use: {
    // 基础URL
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:3000',

    // 浏览器上下文选项
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // 导航超时
    navigationTimeout: 30 * 1000,

    // 操作超时
    actionTimeout: 10 * 1000,

    // 忽略HTTPS错误
    ignoreHTTPSErrors: true,

    // 用户代理
    userAgent: 'Playwright E2E Tests',

    // 视口大小
    viewport: { width: 1280, height: 720 },

    // 语言环境
    locale: 'zh-CN',

    // 时区
    timezoneId: 'Asia/Shanghai',

    // 权限
    permissions: ['geolocation'],

    // 地理位置
    geolocation: { longitude: 116.4074, latitude: 39.9042 }, // 北京

    // 颜色方案
    colorScheme: 'light',
  },

  // 项目配置 - 不同浏览器和设备
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    // 平板测试
    {
      name: 'iPad',
      use: { ...devices['iPad Pro'] },
    },

    // Microsoft Edge
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },

    // Google Chrome
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },

    // 高分辨率测试
    {
      name: 'Desktop Chrome HiDPI',
      use: {
        ...devices['Desktop Chrome HiDPI'],
      },
    },

    // 暗色模式测试
    {
      name: 'Desktop Chrome Dark',
      use: {
        ...devices['Desktop Chrome'],
        colorScheme: 'dark',
      },
    },
  ],

  // 测试服务器配置
  webServer: [
    {
      command: 'npm run dev',
      cwd: '../frontend',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        NODE_ENV: 'test',
      },
    },
    {
      command: 'python -m uvicorn main:app --host 0.0.0.0 --port 8000',
      cwd: '../backend',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        ENVIRONMENT: 'test',
        DATABASE_URL: 'sqlite:///./test.db',
      },
    },
  ],

  // 全局设置和拆卸
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',

  // 测试匹配模式
  testMatch: ['**/*.spec.ts', '**/*.test.ts', '**/*.e2e.ts'],

  // 忽略的文件
  testIgnore: ['**/node_modules/**', '**/dist/**', '**/build/**', '**/.git/**'],

  // 输出目录
  outputDir: 'test-results/',

  // 最大失败数
  maxFailures: process.env.CI ? 10 : undefined,

  // 更新快照
  updateSnapshots: 'missing',

  // 禁用并行执行的测试文件
  fullyParallel: true,

  // 在第一次失败后停止
  forbidOnly: !!process.env.CI,

  // 元数据
  metadata: {
    'test-environment': process.env.NODE_ENV || 'development',
    'base-url': process.env.TEST_BASE_URL || 'http://localhost:3000',
    'browser-versions': {
      chromium: '119.0.6045.105',
      firefox: '119.0',
      webkit: '17.4',
    },
  },

  // 自定义测试配置
  grep: process.env.TEST_GREP ? new RegExp(process.env.TEST_GREP) : undefined,
  grepInvert: process.env.TEST_GREP_INVERT ? new RegExp(process.env.TEST_GREP_INVERT) : undefined,
});

// 环境变量配置说明
/*
环境变量:
- TEST_BASE_URL: 测试基础URL (默认: http://localhost:3000)
- CI: CI环境标识
- NODE_ENV: Node.js环境 (test/development/production)
- TEST_GREP: 测试过滤正则表达式
- TEST_GREP_INVERT: 测试排除正则表达式
- PLAYWRIGHT_BROWSERS_PATH: Playwright浏览器安装路径
- PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: 跳过浏览器下载

使用示例:
- 运行所有测试: npx playwright test
- 运行特定浏览器: npx playwright test --project=chromium
- 运行特定测试: npx playwright test blog.spec.ts
- 调试模式: npx playwright test --debug
- 生成报告: npx playwright show-report
- 录制测试: npx playwright codegen
*/
