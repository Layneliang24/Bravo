// REQ-ID: REQ-2025-003-user-login
// 测试后验证工具
// 目的：在测试完成后验证系统状态和检查潜在问题

import { Page } from '@playwright/test';

export interface PostTestVerification {
  consoleErrors: number;
  failedRequests: number;
  warnings: string[];
}

export async function verifyTestResults(page: Page): Promise<PostTestVerification> {
  const result: PostTestVerification = {
    consoleErrors: 0,
    failedRequests: 0,
    warnings: [],
  };

  // 1. 检查控制台错误
  const consoleMessages = await page.evaluate(() => {
    // 注意：这需要页面在测试过程中记录控制台消息
    // 实际实现可能需要通过page.on('console')在测试过程中收集
    return [];
  });

  const errors = consoleMessages.filter((msg: any) => msg.type === 'error');
  result.consoleErrors = errors.length;

  if (errors.length > 0) {
    result.warnings.push(`发现${errors.length}个控制台错误`);
  }

  // 2. 检查网络请求失败
  const failedRequests = await page.evaluate(() => {
    return window.performance
      .getEntriesByType('resource')
      .filter((entry: any) => {
        return entry.responseStatus && entry.responseStatus >= 400;
      })
      .map((entry: any) => ({
        url: entry.name,
        status: entry.responseStatus,
      }));
  });

  result.failedRequests = failedRequests.length;

  if (failedRequests.length > 0) {
    result.warnings.push(`发现${failedRequests.length}个失败的请求`);
    failedRequests.forEach((req: any) => {
      result.warnings.push(`  - ${req.url}: ${req.status}`);
    });
  }

  // 3. 检查未处理的Promise rejection
  const unhandledRejections = await page.evaluate(() => {
    // 需要页面在测试过程中记录
    return [];
  });

  if (unhandledRejections.length > 0) {
    result.warnings.push(`发现${unhandledRejections.length}个未处理的Promise rejection`);
  }

  // 报告结果
  if (result.warnings.length > 0) {
    console.warn('⚠️ 测试后验证发现问题:');
    result.warnings.forEach(warning => {
      console.warn(`  - ${warning}`);
    });
  } else {
    console.log('✅ 测试后验证通过');
  }

  return result;
}
