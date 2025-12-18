// REQ-ID: REQ-2025-001-example-demo
// TESTCASE-IDS: TC-EXAMPLE_UI-001

import { test, expect } from '@playwright/test';

test('TC-EXAMPLE-003: 示例组件显示API消息（占位）', async ({ page }) => {
  // 说明：该仓库的E2E运行环境由docker-compose提供，这里仅保留最小用例骨架
  await page.goto('/');
  await expect(page).toHaveURL(/\/.*/);
});
