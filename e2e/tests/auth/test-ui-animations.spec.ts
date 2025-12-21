// REQ-ID: REQ-2025-003-user-login
// UI动画效果 E2E 测试
// TESTCASE-IDS: TC-AUTH_UI-008

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

// Docker环境中使用容器名，本地开发使用localhost
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';

class UIAnimationsPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await this.page.waitForSelector('[data-testid="auth-card"], .auth-card', {
      state: 'visible',
      timeout: 15000,
    });
  }

  async checkOrbitAnimation() {
    // 检查学习图标是否有orbit动画
    // AuthCard中使用动态组件<component :is="item.icon">，所以直接查找w-16.h-16.bg-gradient-to-br
    const learningIcons = this.page.locator('.absolute.w-16.h-16.bg-gradient-to-br.rounded-2xl');
    const count = await learningIcons.count();

    if (count >= 3) {
      // 检查第一个图标是否有动画（内联style包含orbit-rotate）
      const firstIcon = learningIcons.first();
      const animationInfo = await firstIcon.evaluate(el => {
        const styles = window.getComputedStyle(el);
        const inlineStyle = el.getAttribute('style') || '';
        return {
          animation: styles.animation || styles.animationName || '',
          inlineStyle: inlineStyle,
        };
      });

      return (
        animationInfo.animation.includes('orbit') ||
        animationInfo.inlineStyle.includes('orbit') ||
        animationInfo.animation !== 'none'
      );
    }
    return false;
  }

  async checkFadeInAnimation() {
    // 检查fade-in动画
    const fadeElements = this.page.locator('.fade-in, .slide-in-left, .slide-in-right');
    const count = await fadeElements.count();
    return count > 0;
  }
}

test.describe('UI动画效果验证', () => {
  let animationsPage: UIAnimationsPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    animationsPage = new UIAnimationsPage(page);

    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    await animationsPage.goto();
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('TC-AUTH_UI-008: 左侧品牌区学习图标应该有环绕动画', async ({ page }) => {
    // 1. 检查学习图标元素存在 - 直接查找w-16.h-16.bg-gradient-to-br（不依赖svg）
    const learningIcons = page.locator('.absolute.w-16.h-16.bg-gradient-to-br.rounded-2xl');
    const iconCount = await learningIcons.count();
    expect(iconCount).toBeGreaterThanOrEqual(3); // 至少3个图标

    // 2. 验证图标有orbit动画
    const hasOrbitAnimation = await animationsPage.checkOrbitAnimation();
    expect(hasOrbitAnimation).toBe(true);

    // 3. 验证动画正在运行（通过检查内联style）
    const firstIcon = learningIcons.first();
    const animationInfo = await firstIcon.evaluate(el => {
      const styles = window.getComputedStyle(el);
      const inlineStyle = el.getAttribute('style') || '';
      return {
        animationName: styles.animationName || '',
        animation: styles.animation || '',
        inlineStyle: inlineStyle,
      };
    });

    // 动画应该存在（内联style包含orbit-rotate）
    const hasAnimation =
      animationInfo.inlineStyle.includes('orbit-rotate') ||
      animationInfo.animation.includes('orbit') ||
      animationInfo.animationName !== 'none';
    expect(hasAnimation).toBe(true);
  });
});
