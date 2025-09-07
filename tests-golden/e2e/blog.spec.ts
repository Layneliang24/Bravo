// 🔒 黄金测试 - E2E博客功能核心测试
// 此文件包含关键的端到端测试，不得随意修改

import { test, expect } from '@playwright/test'

test.describe('🔒 博客E2E黄金测试套件', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000')
  })

  test('应该正确显示博客首页', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('博客')
    await expect(page.locator('.blog-list')).toBeVisible()
  })

  test('应该能够创建新博客文章', async ({ page }) => {
    await page.click('[data-testid="create-blog-btn"]')
    await page.fill('[data-testid="blog-title"]', '测试文章标题')
    await page.fill('[data-testid="blog-content"]', '测试文章内容')
    await page.click('[data-testid="save-blog-btn"]')
    
    await expect(page.locator('.success-message')).toBeVisible()
    await expect(page.locator('.blog-list')).toContainText('测试文章标题')
  })

  test('应该能够编辑现有博客文章', async ({ page }) => {
    await page.click('[data-testid="edit-blog-btn"]:first-child')
    await page.fill('[data-testid="blog-title"]', '编辑后的标题')
    await page.click('[data-testid="save-blog-btn"]')
    
    await expect(page.locator('.success-message')).toBeVisible()
    await expect(page.locator('.blog-list')).toContainText('编辑后的标题')
  })

  test('应该能够删除博客文章', async ({ page }) => {
    const initialCount = await page.locator('.blog-item').count()
    await page.click('[data-testid="delete-blog-btn"]:first-child')
    await page.click('[data-testid="confirm-delete-btn"]')
    
    await expect(page.locator('.blog-item')).toHaveCount(initialCount - 1)
  })

  test('应该正确处理博客搜索功能', async ({ page }) => {
    await page.fill('[data-testid="search-input"]', '测试')
    await page.press('[data-testid="search-input"]', 'Enter')
    
    const searchResults = page.locator('.blog-item')
    await expect(searchResults).toHaveCount(1)
    await expect(searchResults.first()).toContainText('测试')
  })

  test('应该正确处理博客分页功能', async ({ page }) => {
    await expect(page.locator('.pagination')).toBeVisible()
    await page.click('[data-testid="next-page-btn"]')
    
    await expect(page.url()).toContain('page=2')
    await expect(page.locator('.blog-list')).toBeVisible()
  })

  test('应该正确处理博客分类筛选', async ({ page }) => {
    await page.selectOption('[data-testid="category-filter"]', '技术')
    
    const filteredBlogs = page.locator('.blog-item')
    await expect(filteredBlogs.first().locator('.category')).toContainText('技术')
  })

  test('应该正确显示博客详情页面', async ({ page }) => {
    await page.click('.blog-item:first-child .blog-title')
    
    await expect(page.locator('.blog-detail')).toBeVisible()
    await expect(page.locator('.blog-content')).toBeVisible()
    await expect(page.locator('.blog-meta')).toBeVisible()
  })

  test('应该正确处理博客评论功能', async ({ page }) => {
    await page.click('.blog-item:first-child .blog-title')
    await page.fill('[data-testid="comment-input"]', '这是一条测试评论')
    await page.click('[data-testid="submit-comment-btn"]')
    
    await expect(page.locator('.comment-list')).toContainText('这是一条测试评论')
  })

  test('应该正确处理博客点赞功能', async ({ page }) => {
    const likeBtn = page.locator('[data-testid="like-btn"]:first-child')
    const initialLikes = await likeBtn.locator('.like-count').textContent()
    
    await likeBtn.click()
    
    const newLikes = await likeBtn.locator('.like-count').textContent()
    expect(parseInt(newLikes || '0')).toBe(parseInt(initialLikes || '0') + 1)
  })
})
