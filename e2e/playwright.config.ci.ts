import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置 - CI 环境专用
 * 简化配置，专注于稳定性
 */
export default defineConfig({
  // 测试目录
  testDir: './tests',

  // 全局测试超时时间（60秒）
  timeout: 60 * 1000,

  // 每个测试的期望超时时间（10秒）
  expect: {
    timeout: 10000,
  },

  // CI 下减少重试，避免在已知失败场景拖长总时长
  retries: process.env.CI ? 1 : 0,

  // CI 下适度并行，加速执行且避免资源争抢过重
  workers: process.env.CI ? 2 : undefined,

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
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:3001',

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
  },

  // 项目配置 - 只测试主要浏览器
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // CI 在 docker-compose 中已启动 backend-test/frontend-test，这里禁用 Playwright 内置 webServer。
  // 本地调试时保留 webServer，避免影响开发者单独运行 E2E。
  webServer: process.env.CI
    ? undefined
    : [
        {
          command: 'npm run dev -- --port 3001 --host 0.0.0.0',
          cwd: '../frontend',
          port: 3001,
          reuseExistingServer: false, // 本地不重用，避免端口污染
          timeout: 300 * 1000, // 5分钟超时
          env: {
            NODE_ENV: 'test',
            VITE_API_URL: 'http://localhost:8000',
          },
        },
        {
          command: 'python manage.py runserver 0.0.0.0:8000 --settings=bravo.settings.test',
          cwd: '../backend',
          port: 8000,
          reuseExistingServer: false, // 本地不重用，避免端口污染
          timeout: 300 * 1000, // 5分钟超时
          env: {
            ENVIRONMENT: 'test',
            DATABASE_URL: 'sqlite:///./test.db',
            DJANGO_SETTINGS_MODULE: 'bravo.settings.test',
          },
        },
      ],

  // 测试匹配模式 - 只运行基础设施测试
  testMatch: ['**/health.spec.ts', '**/app.spec.ts'],

  // 忽略的文件
  testIgnore: ['**/node_modules/**', '**/dist/**', '**/build/**', '**/.git/**'],

  // 输出目录
  outputDir: 'test-results/',

  // 达到失败阈值后尽快停止，减少无效长时间运行
  maxFailures: process.env.CI ? 3 : undefined,

  // 更新快照
  updateSnapshots: 'missing',

  // 禁用并行执行的测试文件
  fullyParallel: false, // CI环境禁用并行

  // 在第一次失败后停止
  forbidOnly: !!process.env.CI,
});
