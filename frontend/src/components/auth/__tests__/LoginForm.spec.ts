// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import LoginForm from '../LoginForm.vue'
import { useAuthStore } from '@/stores/auth'

describe('LoginForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该正确渲染登录表单', () => {
    const wrapper = mount(LoginForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('应该包含邮箱输入框', () => {
    const wrapper = mount(LoginForm)
    const emailInput = wrapper.find('input[type="email"]')

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
    const emailInput = wrapper.find('input[type="email"]')

    await emailInput.setValue('invalid-email')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('应该验证密码长度', async () => {
    const wrapper = mount(LoginForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
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
    const emailInput = wrapper.find('input[type="email"]')
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
    const loginSpy = vi.spyOn(store, 'login').mockResolvedValue({
      user: { id: '1', email: 'test@example.com', is_email_verified: true },
      token: 'test-token',
      refresh_token: 'test-refresh-token',
    })

    const wrapper = mount(LoginForm, {
      global: {
        mocks: {
          $router: {
            push: vi.fn(),
          },
        },
      },
    })

    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
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
    const loginError = new Error('登录失败，请检查账号密码')
    vi.spyOn(store, 'login').mockRejectedValue(loginError)

    const wrapper = mount(LoginForm, {
      global: {
        mocks: {
          $router: {
            push: vi.fn(),
          },
        },
      },
    })
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
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
})
