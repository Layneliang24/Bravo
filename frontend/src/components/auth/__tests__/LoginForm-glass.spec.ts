// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useRouter } from 'vue-router'
import LoginForm from '../LoginForm.vue'
import { useAuthStore } from '@/stores/auth'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
}))

describe('LoginForm - Glassmorphism Design', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该正确渲染登录表单', () => {
    const wrapper = mount(LoginForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('.username-input').exists()).toBe(true)
    expect(wrapper.find('.password-input').exists()).toBe(true)
    expect(wrapper.find('.login-button').exists()).toBe(true)
  })

  it('应该包含 Username 输入框', () => {
    const wrapper = mount(LoginForm)

    const usernameInput = wrapper.find('.username-input input')
    expect(usernameInput.exists()).toBe(true)
    expect(usernameInput.attributes('type')).toBe('text')
    expect(usernameInput.attributes('placeholder')).toBe('Enter your username')
  })

  it('应该包含 Password 输入框', () => {
    const wrapper = mount(LoginForm)

    const passwordInput = wrapper.find('.password-input input')
    expect(passwordInput.exists()).toBe(true)
    expect(passwordInput.attributes('type')).toBe('password')
    expect(passwordInput.attributes('placeholder')).toBe('Enter your password')
  })

  it('应该显示 "Username" 标签', () => {
    const wrapper = mount(LoginForm)

    const usernameLabel = wrapper.find('.username-label')
    expect(usernameLabel.exists()).toBe(true)
    expect(usernameLabel.text()).toBe('Username')
  })

  it('应该显示 "Password" 标签', () => {
    const wrapper = mount(LoginForm)

    const passwordLabel = wrapper.find('.password-label')
    expect(passwordLabel.exists()).toBe(true)
    expect(passwordLabel.text()).toBe('Password')
  })

  it('应该包含 "Forgot Password?" 链接', () => {
    const wrapper = mount(LoginForm)

    const forgotPassword = wrapper.find('.forgot-password')
    expect(forgotPassword.exists()).toBe(true)
    expect(forgotPassword.text()).toBe('Forgot Password?')
  })

  it('应该包含登录按钮，文本为 "LOGIN"', () => {
    const wrapper = mount(LoginForm)

    const loginButton = wrapper.find('.login-button')
    expect(loginButton.exists()).toBe(true)
    expect(loginButton.text()).toBe('LOGIN')
  })

  it('应该显示 "New to Logo? Register Here" 文本', () => {
    const wrapper = mount(LoginForm)

    const registerText = wrapper.find('.register-text')
    expect(registerText.exists()).toBe(true)
    expect(registerText.text()).toContain('New to Logo? Register Here')
  })

  it('应该包含验证码组件', () => {
    const wrapper = mount(LoginForm)

    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })
    expect(captchaComponent.exists()).toBe(true)
  })

  it('应该验证邮箱格式', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const usernameInput = wrapper.find('.username-input input')

    await usernameInput.setValue('invalid-email')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('应该验证密码长度', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const usernameInput = wrapper.find('.username-input input')
    const passwordInput = wrapper.find('.password-input input')

    await usernameInput.setValue('test@example.com')
    await passwordInput.setValue('12345')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('登录成功时应该调用auth store的login方法', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const loginSpy = vi.spyOn(store, 'login').mockResolvedValue({
      user: { id: '1', email: 'test@example.com', is_email_verified: true },
      token: 'test-token',
      refresh_token: 'test-refresh-token',
    })

    const wrapper = mount(LoginForm)

    const form = wrapper.find('form')
    const usernameInput = wrapper.find('.username-input input')
    const passwordInput = wrapper.find('.password-input input')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await usernameInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(loginSpy).toHaveBeenCalled()
  })

  it('提交时应该禁用登录按钮', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    vi.spyOn(store, 'login').mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    )

    const wrapper = mount(LoginForm)

    const form = wrapper.find('form')
    const loginButton = wrapper.find('.login-button')
    const usernameInput = wrapper.find('.username-input input')
    const passwordInput = wrapper.find('.password-input input')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await usernameInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(loginButton.attributes('disabled')).toBeDefined()
  })
})
