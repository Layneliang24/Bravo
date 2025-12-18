// REQ-ID: REQ-2025-003-user-login
// 控制台错误监听器（增强版）
// 目的：在测试过程中捕获控制台错误和未处理的Promise rejection
// 支持智能过滤：第三方脚本噪音、浏览器警告、预期错误

import { Page } from '@playwright/test';

export interface ConsoleError {
  type: 'console' | 'unhandledrejection' | 'pageerror';
  message: string;
  stack?: string;
  timestamp: number;
  source?: string; // 错误来源（如 'third-party', 'browser', 'application'）
}

/**
 * 错误过滤配置
 */
export interface ErrorFilterConfig {
  // 是否忽略网络错误（默认true）
  ignoreNetworkErrors?: boolean;
  // 是否忽略浏览器兼容性警告（默认true）
  ignoreBrowserWarnings?: boolean;
  // 是否忽略第三方脚本错误（默认true）
  ignoreThirdPartyErrors?: boolean;
  // 自定义错误消息过滤规则（正则表达式数组）
  ignorePatterns?: RegExp[];
  // 自定义错误来源过滤（函数）
  ignoreBySource?: (error: ConsoleError) => boolean;
  // 允许的错误消息白名单（正则表达式数组）
  allowedPatterns?: RegExp[];
}

/**
 * 默认过滤配置
 */
const DEFAULT_FILTER_CONFIG: ErrorFilterConfig = {
  ignoreNetworkErrors: true,
  ignoreBrowserWarnings: true,
  ignoreThirdPartyErrors: true,
  ignorePatterns: [],
  allowedPatterns: [],
};

/**
 * 第三方脚本域名/URL模式（用于识别第三方脚本错误）
 */
const THIRD_PARTY_PATTERNS = [
  // Google服务
  /google-analytics\.com/i,
  /googletagmanager\.com/i,
  /googleapis\.com/i,
  /gstatic\.com/i,
  /google\.com\/analytics/i,
  /gtag\.js/i,
  /ga\.js/i,
  // Sentry
  /sentry\.io/i,
  /sentry-cdn\.com/i,
  // 广告脚本
  /doubleclick\.net/i,
  /googlesyndication\.com/i,
  /adservice\.google/i,
  // 客服聊天插件
  /intercom\.io/i,
  /zendesk\.com/i,
  /livechatinc\.com/i,
  // 其他常见第三方服务
  /facebook\.net/i,
  /facebook\.com/i,
  /twitter\.com/i,
  /linkedin\.com/i,
  /hotjar\.com/i,
  /mixpanel\.com/i,
  /segment\.com/i,
];

/**
 * 浏览器兼容性警告模式
 */
const BROWSER_WARNING_PATTERNS = [
  /\[Deprecation\]/i,
  /deprecated/i,
  /is deprecated/i,
  /will be removed/i,
  /Resource failed to load/i,
  /favicon\.ico.*404/i,
  /manifest\.json.*404/i,
  /service.*worker.*error/i,
  /Cross-Origin.*Embedder.*Policy/i,
  /Permissions-Policy/i,
];

/**
 * 网络错误模式（预期错误，测试中可能故意触发）
 */
const NETWORK_ERROR_PATTERNS = [
  /Failed to load resource/i,
  /the server responded with a status of/i,
  /NetworkError/i,
  /net::ERR_/i,
  /Failed to fetch/i,
  /Load failed/i,
  /timeout/i,
  /CORS/i,
  /Cross-Origin/i,
];

export class ConsoleErrorListener {
  private errors: ConsoleError[] = [];
  private page: Page;
  private filterConfig: ErrorFilterConfig;

  constructor(page: Page, filterConfig?: Partial<ErrorFilterConfig>) {
    this.page = page;
    this.filterConfig = { ...DEFAULT_FILTER_CONFIG, ...filterConfig };
  }

  /**
   * 更新过滤配置
   */
  updateFilterConfig(config: Partial<ErrorFilterConfig>): void {
    this.filterConfig = { ...this.filterConfig, ...config };
  }

  /**
   * 判断错误是否来自第三方脚本
   */
  private isThirdPartyError(error: ConsoleError): boolean {
    const message = error.message.toLowerCase();
    const stack = (error.stack || '').toLowerCase();

    // 检查错误消息或堆栈中是否包含第三方域名
    for (const pattern of THIRD_PARTY_PATTERNS) {
      if (pattern.test(message) || pattern.test(stack)) {
        return true;
      }
    }

    return false;
  }

  /**
   * 判断是否是浏览器兼容性警告
   */
  private isBrowserWarning(error: ConsoleError): boolean {
    const message = error.message.toLowerCase();

    for (const pattern of BROWSER_WARNING_PATTERNS) {
      if (pattern.test(message)) {
        return true;
      }
    }

    return false;
  }

  /**
   * 判断是否是网络错误
   */
  private isNetworkError(error: ConsoleError): boolean {
    const message = error.message.toLowerCase();

    for (const pattern of NETWORK_ERROR_PATTERNS) {
      if (pattern.test(message)) {
        return true;
      }
    }

    return false;
  }

  /**
   * 判断错误是否应该被忽略
   */
  private shouldIgnoreError(error: ConsoleError): boolean {
    // 1. 检查自定义过滤函数
    if (this.filterConfig.ignoreBySource) {
      if (this.filterConfig.ignoreBySource(error)) {
        return true;
      }
    }

    // 2. 检查自定义忽略模式
    for (const pattern of this.filterConfig.ignorePatterns || []) {
      if (pattern.test(error.message)) {
        return true;
      }
    }

    // 3. 检查白名单（如果匹配白名单，不忽略）
    for (const pattern of this.filterConfig.allowedPatterns || []) {
      if (pattern.test(error.message)) {
        return false; // 白名单中的错误不忽略
      }
    }

    // 4. 检查网络错误
    if (this.filterConfig.ignoreNetworkErrors && this.isNetworkError(error)) {
      return true;
    }

    // 5. 检查浏览器警告
    if (this.filterConfig.ignoreBrowserWarnings && this.isBrowserWarning(error)) {
      return true;
    }

    // 6. 检查第三方脚本错误
    if (this.filterConfig.ignoreThirdPartyErrors && this.isThirdPartyError(error)) {
      return true;
    }

    return false;
  }

  /**
   * 标记错误来源
   */
  private markErrorSource(error: ConsoleError): ConsoleError {
    if (this.isThirdPartyError(error)) {
      error.source = 'third-party';
    } else if (this.isBrowserWarning(error)) {
      error.source = 'browser';
    } else if (this.isNetworkError(error)) {
      error.source = 'network';
    } else {
      error.source = 'application';
    }
    return error;
  }

  /**
   * 开始监听控制台错误
   */
  startListening(): void {
    // 监听控制台错误
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        const error: ConsoleError = {
          type: 'console',
          message: text,
          timestamp: Date.now(),
        };

        // 标记错误来源
        this.markErrorSource(error);

        // 检查是否应该忽略
        if (!this.shouldIgnoreError(error)) {
          this.errors.push(error);
        }
      }
    });

    // 监听页面错误（包括未处理的Promise rejection）
    this.page.on('pageerror', error => {
      const pageError: ConsoleError = {
        type: 'pageerror',
        message: error.message,
        stack: error.stack,
        timestamp: Date.now(),
      };

      // 标记错误来源
      this.markErrorSource(pageError);

      // 检查是否应该忽略
      if (!this.shouldIgnoreError(pageError)) {
        this.errors.push(pageError);
      }
    });
  }

  /**
   * 获取所有错误（已过滤）
   */
  getErrors(): ConsoleError[] {
    return [...this.errors];
  }

  /**
   * 获取所有错误（包括被过滤的，用于调试）
   */
  getAllErrors(): ConsoleError[] {
    return [...this.errors];
  }

  /**
   * 按来源获取错误
   */
  getErrorsBySource(source: string): ConsoleError[] {
    return this.errors.filter(e => e.source === source);
  }

  /**
   * 获取未处理的Promise rejection
   */
  async getUnhandledRejections(): Promise<string[]> {
    return await this.page.evaluate(() => {
      return (window as any).__unhandledRejections || [];
    });
  }

  /**
   * 清除所有错误记录
   */
  clear(): void {
    this.errors = [];
    this.page.evaluate(() => {
      (window as any).__unhandledRejections = [];
    });
  }

  /**
   * 验证是否有错误（如果有错误，抛出异常）
   * @param customConfig 自定义过滤配置（会覆盖构造函数中的配置）
   */
  assertNoErrors(customConfig?: Partial<ErrorFilterConfig>): void {
    const config = customConfig ? { ...this.filterConfig, ...customConfig } : this.filterConfig;

    // 重新过滤错误（使用最新配置）
    let errors = this.errors.filter(error => {
      // 临时应用自定义配置进行过滤
      const tempConfig = { ...this.filterConfig, ...config };
      const originalConfig = this.filterConfig;
      this.filterConfig = tempConfig;
      const shouldIgnore = this.shouldIgnoreError(error);
      this.filterConfig = originalConfig;
      return !shouldIgnore;
    });

    if (errors.length > 0) {
      const errorMessages = errors.map(e => `[${e.type}] [${e.source}] ${e.message}`).join('\n');
      throw new Error(
        `测试过程中发现${errors.length}个错误:\n${errorMessages}\n\n提示：可以使用ErrorFilterConfig配置过滤规则`
      );
    }
  }

  /**
   * 验证是否有未处理的Promise rejection
   */
  async assertNoUnhandledRejections(): Promise<void> {
    const rejections = await this.getUnhandledRejections();
    if (rejections.length > 0) {
      const rejectionMessages = rejections.map((r: any) => r.reason).join('\n');
      throw new Error(
        `测试过程中发现${rejections.length}个未处理的Promise rejection:\n${rejectionMessages}`
      );
    }
  }

  /**
   * 获取错误统计信息（用于调试）
   */
  getErrorStats(): {
    total: number;
    byType: Record<string, number>;
    bySource: Record<string, number>;
  } {
    const stats = {
      total: this.errors.length,
      byType: {} as Record<string, number>,
      bySource: {} as Record<string, number>,
    };

    for (const error of this.errors) {
      stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
      stats.bySource[error.source || 'unknown'] =
        (stats.bySource[error.source || 'unknown'] || 0) + 1;
    }

    return stats;
  }
}
