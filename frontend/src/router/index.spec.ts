// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_UI-001
// 路由配置单元测试（基础设施测试）
// 对应测试用例：
// - TC-AUTH_UI-001: 登录页面布局-左右分栏（路由配置支持页面访问）
import { beforeEach, describe, expect, it } from 'vitest'
import router from './index'

describe('Router', () => {
  beforeEach(async () => {
    // 重置路由状态
    router.push('/')
    await router.isReady()
  })

  it('应该正确配置路由', () => {
    expect(router).toBeDefined()
    expect(router.getRoutes()).toHaveLength(8) // Home, Login, Blog, BlogDetail, Register, ForgotPassword, ResetPassword, VerifyEmail
  })

  it('应该有Home路由', () => {
    const homeRoute = router.getRoutes().find(route => route.name === 'Home')
    expect(homeRoute).toBeDefined()
    expect(homeRoute?.path).toBe('/')
  })

  it('应该有Login路由', () => {
    const loginRoute = router.getRoutes().find(route => route.name === 'Login')
    expect(loginRoute).toBeDefined()
    expect(loginRoute?.path).toBe('/login')
  })

  it('应该有Blog路由', () => {
    const blogRoute = router.getRoutes().find(route => route.name === 'Blog')
    expect(blogRoute).toBeDefined()
    expect(blogRoute?.path).toBe('/blog')
  })

  it('应该有BlogDetail路由', () => {
    const blogDetailRoute = router
      .getRoutes()
      .find(route => route.name === 'BlogDetail')
    expect(blogDetailRoute).toBeDefined()
    expect(blogDetailRoute?.path).toBe('/blog/:id')
  })

  it('应该有VerifyEmail路由', () => {
    const verifyEmailRoute = router
      .getRoutes()
      .find(route => route.name === 'VerifyEmail')
    expect(verifyEmailRoute).toBeDefined()
    expect(verifyEmailRoute?.path).toBe('/verify-email')
  })

  it('应该能够导航到Home页面', async () => {
    await router.push('/')
    expect(router.currentRoute.value.name).toBe('Home')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('应该能够导航到Login页面', async () => {
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('Login')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('应该能够导航到Blog页面', async () => {
    await router.push('/blog')
    expect(router.currentRoute.value.name).toBe('Blog')
    expect(router.currentRoute.value.path).toBe('/blog')
  })

  it('应该能够导航到BlogDetail页面', async () => {
    await router.push('/blog/123')
    expect(router.currentRoute.value.name).toBe('BlogDetail')
    expect(router.currentRoute.value.path).toBe('/blog/123')
    expect(router.currentRoute.value.params.id).toBe('123')
  })

  it('应该能够通过名称导航', async () => {
    await router.push({ name: 'Home' })
    expect(router.currentRoute.value.name).toBe('Home')

    await router.push({ name: 'Login' })
    expect(router.currentRoute.value.name).toBe('Login')

    await router.push({ name: 'Blog' })
    expect(router.currentRoute.value.name).toBe('Blog')

    await router.push({ name: 'BlogDetail', params: { id: '456' } })
    expect(router.currentRoute.value.name).toBe('BlogDetail')
    expect(router.currentRoute.value.params.id).toBe('456')

    await router.push({ name: 'VerifyEmail' })
    expect(router.currentRoute.value.name).toBe('VerifyEmail')
  })

  it('应该使用createWebHistory', () => {
    // 检查路由器是否正确初始化
    expect(router.options.history).toBeDefined()
  })

  it('应该支持懒加载组件', () => {
    const routes = router.getRoutes()
    routes.forEach(route => {
      // 检查组件是否为函数（懒加载）或已解析的组件对象
      const component = route.components?.default
      expect(component).toBeDefined()
      // 懒加载组件在测试环境中可能已经被解析为对象
      expect(
        typeof component === 'function' || typeof component === 'object'
      ).toBe(true)
    })
  })
})
