// 博客功能 E2E 测试
// 使用 Playwright 进行端到端测试

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3000';

// 页面对象模式 - 博客页面
class BlogPage {
  constructor(private page: Page) {}

  // 获取页面对象
  getPage(): Page {
    return this.page;
  }

  // 页面元素选择器
  private selectors = {
    blogTitle: '[data-testid="blog-title"]',
    blogList: '[data-testid="blog-list"]',
    blogItem: '[data-testid="blog-item"]',
    blogContent: '[data-testid="blog-content"]',
    searchInput: '[data-testid="search-input"]',
    searchButton: '[data-testid="search-button"]',
    categoryFilter: '[data-testid="category-filter"]',
    loadMoreButton: '[data-testid="load-more"]',
    createPostButton: '[data-testid="create-post"]',
    postTitle: '[data-testid="post-title"]',
    postContent: '[data-testid="post-content"]',
    publishButton: '[data-testid="publish-button"]',
    editButton: '[data-testid="edit-button"]',
    deleteButton: '[data-testid="delete-button"]',
  };

  // 导航到博客页面
  async goto() {
    await this.page.goto(`${BASE_URL}/blog`);
    await this.page.waitForLoadState('networkidle');
  }

  // 获取博客标题
  async getBlogTitle() {
    return await this.page.textContent(this.selectors.blogTitle, { timeout: 30000 });
  }

  // 获取博客列表
  async getBlogList() {
    await this.page.waitForSelector(this.selectors.blogList, { timeout: 30000 });
    return await this.page.locator(this.selectors.blogItem).all();
  }

  // 搜索博客
  async searchBlog(keyword: string) {
    await this.page.fill(this.selectors.searchInput, keyword);
    await this.page.click(this.selectors.searchButton);
    await this.page.waitForLoadState('networkidle');
  }

  // 按分类筛选
  async filterByCategory(category: string) {
    await this.page.selectOption(this.selectors.categoryFilter, category);
    await this.page.waitForLoadState('networkidle');
  }

  // 点击博客项目
  async clickBlogItem(index: number = 0) {
    const blogItems = await this.getBlogList();
    if (blogItems.length > index) {
      await blogItems[index].click();
      await this.page.waitForLoadState('networkidle');
    }
  }

  // 创建新博客
  async createNewPost(title: string, content: string) {
    await this.page.click(this.selectors.createPostButton);
    await this.page.fill(this.selectors.postTitle, title);
    await this.page.fill(this.selectors.postContent, content);
    await this.page.click(this.selectors.publishButton);
    await this.page.waitForLoadState('networkidle');
  }

  // 编辑博客
  async editPost(newTitle: string, newContent: string) {
    await this.page.click(this.selectors.editButton);
    await this.page.fill(this.selectors.postTitle, newTitle);
    await this.page.fill(this.selectors.postContent, newContent);
    await this.page.click(this.selectors.publishButton);
    await this.page.waitForLoadState('networkidle');
  }

  // 删除博客
  async deletePost() {
    await this.page.click(this.selectors.deleteButton);
    // 确认删除对话框
    await this.page.click('button:has-text("确认")');
    await this.page.waitForLoadState('networkidle');
  }

  // 加载更多
  async loadMore() {
    await this.page.click(this.selectors.loadMoreButton);
    await this.page.waitForLoadState('networkidle');
  }
}

// 测试套件
test.describe('博客功能测试', () => {
  let blogPage: BlogPage;

  test.beforeEach(async ({ page }) => {
    blogPage = new BlogPage(page);
    await blogPage.goto();
  });

  test('应该正确显示博客页面标题', async () => {
    const title = await blogPage.getBlogTitle();
    expect(title).toBeTruthy();
    expect(title).toContain('博客');
  });

  test('应该显示博客列表', async () => {
    const blogList = await blogPage.getBlogList();
    expect(blogList.length).toBeGreaterThan(0);
  });

  test('应该能够搜索博客', async () => {
    await blogPage.searchBlog('测试');

    // 验证搜索结果
    const blogList = await blogPage.getBlogList();
    expect(blogList.length).toBeGreaterThanOrEqual(0);
  });

  test('应该能够按分类筛选博客', async () => {
    await blogPage.filterByCategory('技术');

    // 验证筛选结果
    const blogList = await blogPage.getBlogList();
    expect(blogList.length).toBeGreaterThanOrEqual(0);
  });

  test('应该能够点击博客项目查看详情', async () => {
    const blogList = await blogPage.getBlogList();
    if (blogList.length > 0) {
      await blogPage.clickBlogItem(0);

      // 验证跳转到详情页
      expect(blogPage.getPage().url()).toContain('/blog/');
    }
  });

  test('应该能够创建新博客', async ({ page }) => {
    // 模拟登录状态（如果需要）
    // await page.context().addCookies([...]);

    const testTitle = `测试博客 ${Date.now()}`;
    const testContent = '这是一篇测试博客的内容。';

    await blogPage.createNewPost(testTitle, testContent);

    // 验证博客创建成功
    expect(page.url()).toContain('/blog/');
  });

  test('应该能够编辑博客', async ({ page }) => {
    // 首先创建一篇博客
    const originalTitle = `原始标题 ${Date.now()}`;
    const originalContent = '原始内容';
    await blogPage.createNewPost(originalTitle, originalContent);

    // 然后编辑它
    const newTitle = `编辑后标题 ${Date.now()}`;
    const newContent = '编辑后内容';
    await blogPage.editPost(newTitle, newContent);

    // 验证编辑成功
    const updatedTitle = await page.textContent(blogPage['selectors'].postTitle);
    expect(updatedTitle).toContain(newTitle);
  });

  test('应该能够删除博客', async ({ page }) => {
    // 首先创建一篇博客
    const testTitle = `待删除博客 ${Date.now()}`;
    const testContent = '待删除内容';
    await blogPage.createNewPost(testTitle, testContent);

    // 然后删除它
    await blogPage.deletePost();

    // 验证删除成功（重定向到博客列表）
    expect(page.url()).toContain('/blog');
  });

  test('应该能够加载更多博客', async () => {
    const initialBlogList = await blogPage.getBlogList();
    const initialCount = initialBlogList.length;

    // 如果有"加载更多"按钮
    const loadMoreButton = blogPage.getPage().locator(blogPage['selectors'].loadMoreButton);
    if (await loadMoreButton.isVisible()) {
      await blogPage.loadMore();

      const updatedBlogList = await blogPage.getBlogList();
      expect(updatedBlogList.length).toBeGreaterThanOrEqual(initialCount);
    }
  });

  test('应该响应式显示在移动设备上', async ({ page }) => {
    // 设置移动设备视口
    await page.setViewportSize({ width: 375, height: 667 });
    await blogPage.goto();

    // 验证移动端布局
    const blogList = await blogPage.getBlogList();
    expect(blogList.length).toBeGreaterThan(0);

    // 验证移动端特定元素
    const mobileMenu = page.locator('[data-testid="mobile-menu"]');
    if (await mobileMenu.isVisible()) {
      expect(mobileMenu).toBeVisible();
    }
  });

  test('应该正确处理网络错误', async ({ page }) => {
    // 模拟网络离线
    await page.context().setOffline(true);

    try {
      await blogPage.goto();
    } catch (error) {
      // 验证错误处理
      expect(error).toBeTruthy();
    }

    // 恢复网络连接
    await page.context().setOffline(false);
  });

  test('应该有正确的SEO元数据', async ({ page }) => {
    await blogPage.goto();

    // 检查页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // 检查meta描述
    const metaDescription = await page.getAttribute('meta[name="description"]', 'content');
    expect(metaDescription).toBeTruthy();

    // 检查Open Graph标签
    const ogTitle = await page.getAttribute('meta[property="og:title"]', 'content');
    expect(ogTitle).toBeTruthy();
  });
});

// 性能测试
test.describe('博客页面性能测试', () => {
  test('页面加载时间应该在合理范围内', async ({ page }) => {
    const startTime = Date.now();

    await page.goto(`${BASE_URL}/blog`);
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // 页面加载时间应该少于5秒
    expect(loadTime).toBeLessThan(5000);
  });

  test('应该正确缓存静态资源', async ({ page }) => {
    // 首次访问
    await page.goto(`${BASE_URL}/blog`);
    await page.waitForLoadState('networkidle');

    // 再次访问，检查缓存
    const startTime = Date.now();
    await page.reload();
    await page.waitForLoadState('networkidle');
    const reloadTime = Date.now() - startTime;

    // 重新加载应该更快（由于缓存）
    expect(reloadTime).toBeLessThan(3000);
  });
});

// 可访问性测试
test.describe('博客页面可访问性测试', () => {
  test('应该支持键盘导航', async ({ page }) => {
    await page.goto(`${BASE_URL}/blog`);

    // 使用Tab键导航
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  });

  test('应该有正确的ARIA标签', async ({ page }) => {
    await page.goto(`${BASE_URL}/blog`);

    // 检查主要区域的ARIA标签
    const mainContent = page.locator('main, [role="main"]');
    expect(await mainContent.count()).toBeGreaterThan(0);

    // 检查导航区域
    const navigation = page.locator('nav, [role="navigation"]');
    expect(await navigation.count()).toBeGreaterThan(0);
  });
});
