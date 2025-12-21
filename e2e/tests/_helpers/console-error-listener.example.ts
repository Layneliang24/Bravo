// REQ-ID: REQ-2025-003-user-login
// 控制台错误监听器使用示例
// 展示如何配置和使用 ConsoleErrorListener 处理各种场景

import { test } from '@playwright/test';
import { ConsoleErrorListener } from './console-error-listener';

/**
 * 示例1：基础使用（默认配置）
 * 自动过滤：网络错误、浏览器警告、第三方脚本错误
 */
test.describe('示例1：基础使用', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    // 使用默认配置（自动过滤所有噪音）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();
  });

  test.afterEach(async () => {
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('测试功能', async ({ page }) => {
    // 测试代码...
  });
});

/**
 * 示例2：严格模式（不过滤任何错误）
 * 适用于：需要捕获所有错误的场景
 */
test.describe('示例2：严格模式', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    // 不过滤任何错误
    errorListener = new ConsoleErrorListener(page, {
      ignoreNetworkErrors: false,
      ignoreBrowserWarnings: false,
      ignoreThirdPartyErrors: false,
    });
    errorListener.startListening();
  });

  test.afterEach(async () => {
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('测试功能', async ({ page }) => {
    // 测试代码...
  });
});

/**
 * 示例3：自定义过滤规则
 * 适用于：有特定错误需要忽略的场景
 */
test.describe('示例3：自定义过滤规则', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    errorListener = new ConsoleErrorListener(page, {
      ignorePatterns: [/特定的错误消息/i, /另一个错误模式/i],
      // 使用函数过滤
      ignoreBySource: error => {
        // 忽略特定来源的错误
        if (error.source === 'third-party' && error.message.includes('特定第三方错误')) {
          return true;
        }
        return false;
      },
    });
    errorListener.startListening();
  });

  test.afterEach(async () => {
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('测试功能', async ({ page }) => {
    // 测试代码...
  });
});

/**
 * 示例4：白名单模式
 * 适用于：只关注特定类型的错误
 */
test.describe('示例4：白名单模式', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    errorListener = new ConsoleErrorListener(page, {
      // 只捕获匹配白名单的错误（即使匹配忽略规则）
      allowedPatterns: [/必须捕获的错误/i, /关键业务错误/i],
    });
    errorListener.startListening();
  });

  test.afterEach(async () => {
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('测试功能', async ({ page }) => {
    // 测试代码...
  });
});

/**
 * 示例5：动态更新配置
 * 适用于：不同测试用例需要不同过滤规则
 */
test.describe('示例5：动态更新配置', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();
  });

  test('测试用例1：需要捕获网络错误', async ({ page }) => {
    // 临时更新配置：不忽略网络错误
    errorListener.updateFilterConfig({
      ignoreNetworkErrors: false,
    });

    // 执行测试...
    // 此时网络错误会被捕获

    // 验证错误（使用临时配置）
    errorListener.assertNoErrors({
      ignoreNetworkErrors: false,
    });
  });

  test('测试用例2：忽略网络错误', async ({ page }) => {
    // 恢复默认配置：忽略网络错误
    errorListener.updateFilterConfig({
      ignoreNetworkErrors: true,
    });

    // 执行测试...
    // 此时网络错误会被忽略

    // 验证错误（使用默认配置）
    errorListener.assertNoErrors();
  });
});

/**
 * 示例6：错误统计和调试
 * 适用于：调试时查看错误详情
 */
test.describe('示例6：错误统计和调试', () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();
  });

  test.afterEach(async () => {
    // 获取错误统计
    const stats = errorListener.getErrorStats();
    console.log('错误统计:', stats);
    // 输出示例：
    // {
    //   total: 2,
    //   byType: { console: 1, pageerror: 1 },
    //   bySource: { application: 2 }
    // }

    // 按来源获取错误
    const appErrors = errorListener.getErrorsBySource('application');
    const thirdPartyErrors = errorListener.getErrorsBySource('third-party');

    console.log('业务代码错误:', appErrors.length);
    console.log('第三方脚本错误:', thirdPartyErrors.length);

    // 验证错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('测试功能', async ({ page }) => {
    // 测试代码...
  });
});
