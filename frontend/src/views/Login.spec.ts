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
    // 清除所有mock调用记录
    vi.clearAllMocks()

    // 使用字符串stubs，避免命名规则冲突，并产出 *-stub 标签
    wrapper = mount(Login, {
      global: {
        stubs: ['el-card', 'el-form', 'el-form-item', 'el-input', 'el-button'],
      },
    })
  })

  it('应该正确渲染登录表单', () => {
    // 检查标题
    expect(wrapper.find('h2').text()).toBe('登录')

    // 使用 data-testid 选择器，避免依赖具体渲染实现
    expect(wrapper.find('[data-testid="login-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="login-button"]').exists()).toBe(true)
  })

  it('应该能够输入用户名和密码', async () => {
    // 直接测试响应式数据
    expect(wrapper.vm.loginForm.username).toBe('')
    expect(wrapper.vm.loginForm.password).toBe('')

    // 模拟用户输入
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 验证数据绑定
    expect(wrapper.vm.loginForm.username).toBe('testuser')
    expect(wrapper.vm.loginForm.password).toBe('testpassword')
  })

  it('当用户名和密码都填写时，点击登录应该跳转到首页', async () => {
    // 设置表单数据
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证路由跳转
    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('当用户名为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（用户名为空）
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当密码为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（密码为空）
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当用户名和密码都为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（都为空）
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('应该有正确的CSS样式类', () => {
    expect(wrapper.find('.login').exists()).toBe(true)
    expect(wrapper.find('.login-card').exists()).toBe(true)
  })
})
