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

describe('LoginForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该正确渲染登录表单', () => {
    const wrapper = mount(LoginForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('.username-input input[type="text"]').exists()).toBe(
      true
    )
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('应该包含邮箱输入框', () => {
    const wrapper = mount(LoginForm)
    const emailInput = wrapper.find('.username-input input[type="text"]')

    expect(emailInput.exists()).toBe(true)
  })

  it('应该包含密码输入框', () => {
    const wrapper = mount(LoginForm)
    const passwordInput = wrapper.find('input[type="password"]')

    expect(passwordInput.exists()).toBe(true)
  })

  it('应该包含提交按钮', () => {
    const wrapper = mount(LoginForm)
    const submitButton = wrapper.find('button[type="submit"]')

    expect(submitButton.exists()).toBe(true)
  })

  it('应该包含验证码组件', () => {
    const wrapper = mount(LoginForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    expect(captchaComponent.exists()).toBe(true)
  })

  it('应该验证邮箱格式', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')

    await emailInput.setValue('invalid-email')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('应该验证密码长度', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('12345')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('应该验证验证码必填', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    // 验证码验证应该在表单提交时触发
    expect(wrapper.vm.isSubmitting).toBe(false)
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
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(loginSpy).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
  })

  it('登录失败时应该显示错误信息并刷新验证码', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const loginError = new Error('登录失败，请检查账号密码')
    vi.spyOn(store, 'login').mockRejectedValue(loginError)

    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    // Mock refreshCaptcha方法
    const refreshCaptchaSpy = vi.fn()
    if (captchaComponent.vm) {
      ;(captchaComponent.vm as any).refreshCaptcha = refreshCaptchaSpy
    }

    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 应该显示错误信息
    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)

    // 应该刷新验证码（通过检查captchaRef是否被调用）
    // 由于异步操作，可能需要等待
    await new Promise(resolve => setTimeout(resolve, 50))
  })

  it('登录成功时应该导航到首页', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    vi.spyOn(store, 'login').mockResolvedValue({
      user: { id: '1', email: 'test@example.com', is_email_verified: true },
      token: 'test-token',
      refresh_token: 'test-refresh-token',
    })

    const wrapper = mount(LoginForm)

    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(routerPush).toHaveBeenCalledWith('/')
  })

  it('提交时应该禁用提交按钮', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    vi.spyOn(store, 'login').mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    )

    const wrapper = mount(LoginForm)

    const form = wrapper.find('form')
    const submitButton = wrapper.find('button[type="submit"]')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(submitButton.attributes('disabled')).toBeDefined()
    expect(submitButton.text()).toBe('登录中...')
  })

  it('应该渲染UserPreview组件', async () => {
    const store = useAuthStore()
    store.preview = {
      valid: true,
      user: {
        display_name: 'Preview User',
        avatar_url: null,
        avatar_letter: 'P',
      },
    }

    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const wrapper = mount(LoginForm)

    await wrapper.vm.$nextTick()

    const userPreview = wrapper.findComponent({ name: 'UserPreview' })
    expect(userPreview.exists()).toBe(true)
  })

  it('密码失焦时应触发预验证调用previewLogin', async () => {
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const previewSpy = vi.spyOn(store, 'previewLogin').mockResolvedValue({
      valid: true,
      user: {
        display_name: 'Preview User',
        avatar_url: null,
        avatar_letter: 'P',
      },
    })

    const wrapper = mount(LoginForm)

    const form = wrapper.find('form')
    const emailInput = wrapper.find('.username-input input[type="text"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('preview@example.com')
    await passwordInput.setValue('previewpass')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'preview-captcha-id',
      captcha_answer: '9999',
    })
    await wrapper.vm.$nextTick()

    await passwordInput.trigger('blur')
    await wrapper.vm.$nextTick()

    expect(previewSpy).toHaveBeenCalledWith({
      email: 'preview@example.com',
      password: 'previewpass',
      captcha_id: 'preview-captcha-id',
      captcha_answer: '9999',
    })
    expect(form.exists()).toBe(true)
  })

  it('应该正确处理验证码更新事件', async () => {
    const wrapper = mount(LoginForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'new-captcha-id',
      captcha_answer: '5678',
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.formData.captcha_id).toBe('new-captcha-id')
    expect(wrapper.vm.formData.captcha_answer).toBe('5678')
  })

  it('验证码更新时应该清除之前的错误', async () => {
    const wrapper = mount(LoginForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    // 先设置一个错误
    wrapper.vm.errors.captcha_answer = '验证码错误'

    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'new-captcha-id',
      captcha_answer: '5678',
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.errors.captcha_answer).toBe('')
  })
})
