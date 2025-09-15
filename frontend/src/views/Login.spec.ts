import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Login from './Login.vue'

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', async () => {
  const actual = (await vi.importActual('vue-router')) as Record<
    string,
    unknown
  >
  return {
    ...actual,
    useRouter: (): { push: typeof mockPush } => ({
      push: mockPush,
    }),
  }
})

describe('Login.vue', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = mount(Login, {
      global: {
        // 🔥 关键修复：不要stub el-card，让它正常渲染，只stub内部组件
        stubs: ['el-form', 'el-form-item', 'el-input', 'el-button'],
      },
    })
  })

  it('应该正确渲染登录表单', () => {
    // DEBUG: 打印实际DOM结构来分析问题
    console.log('=== ACTUAL DOM STRUCTURE ===')
    console.log(wrapper.html())
    console.log('=== END DOM STRUCTURE ===')

    // el-card真实渲染，其他组件用stub
    const formSelector = 'el-form-stub,[data-testid="login-form"]'
    const buttonSelector = 'el-button-stub,[data-testid="login-button"]'
    const cardSelector = 'el-card' // Element Plus标签选择器

    expect(wrapper.find(cardSelector).exists()).toBe(true)
    expect(wrapper.find(formSelector).exists()).toBe(true)
    expect(wrapper.find(buttonSelector).exists()).toBe(true)
  })

  it('应该能够输入用户名和密码', async () => {
    expect(wrapper.vm.loginForm.username).toBe('')
    expect(wrapper.vm.loginForm.password).toBe('')

    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.loginForm.username).toBe('testuser')
    expect(wrapper.vm.loginForm.password).toBe('testpassword')
  })

  it('当用户名和密码都填写时，点击登录应该跳转到首页', async () => {
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogin()

    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('当用户名为空时，点击登录不应该跳转', async () => {
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogin()

    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当密码为空时，点击登录不应该跳转', async () => {
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogin()

    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当用户名和密码都为空时，点击登录不应该跳转', async () => {
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    await wrapper.vm.handleLogin()

    expect(mockPush).not.toHaveBeenCalled()
  })

  it('应该有正确的CSS样式类', () => {
    expect(wrapper.find('.login').exists()).toBe(true)
    expect(wrapper.find('.login-card').exists()).toBe(true)
  })
})
