// REQ-ID: REQ-2025-003-user-login
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useRouter } from 'vue-router'
import RegisterForm from '../RegisterForm.vue'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
}))

describe('RegisterForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)
  })

  it('应该正确渲染注册表单', () => {
    const wrapper = mount(RegisterForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('应该包含邮箱输入框', () => {
    const wrapper = mount(RegisterForm)
    const emailInput = wrapper.find('input[type="email"]')

    expect(emailInput.exists()).toBe(true)
  })

  it('应该包含密码输入框', () => {
    const wrapper = mount(RegisterForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    expect(passwordInputs.length).toBeGreaterThanOrEqual(2)
  })

  it('应该包含提交按钮', () => {
    const wrapper = mount(RegisterForm)
    const submitButton = wrapper.find('button[type="submit"]')

    expect(submitButton.exists()).toBe(true)
  })

  it('应该包含验证码组件', () => {
    const wrapper = mount(RegisterForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    expect(captchaComponent.exists()).toBe(true)
  })

  it('应该包含密码强度组件', () => {
    const wrapper = mount(RegisterForm)
    const passwordStrengthComponent = wrapper.findComponent({
      name: 'PasswordStrength',
    })

    expect(passwordStrengthComponent.exists()).toBe(true)
  })

  it('注册成功时应该调用auth store的register方法', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    const registerSpy = vi.spyOn(store, 'register').mockResolvedValue({
      user: { id: '1', email: 'test@example.com', is_email_verified: false },
      token: 'test-token',
      refresh_token: 'test-refresh-token',
    })

    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('password123')
    await passwordInputs[1].setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(registerSpy).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
      password_confirm: 'password123',
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
  })

  it('注册失败时应该显示错误信息并刷新验证码', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    const registerError = new Error('注册失败，邮箱已存在')
    vi.spyOn(store, 'register').mockRejectedValue(registerError)

    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('password123')
    await passwordInputs[1].setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('应该验证密码和确认密码是否一致', async () => {
    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('password123')
    await passwordInputs[1].setValue('password456')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('应该验证邮箱格式', async () => {
    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')

    await emailInput.setValue('invalid-email')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('应该验证密码长度', async () => {
    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('12345')
    await passwordInputs[1].setValue('12345')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessages = wrapper.findAll('.error-message')
    expect(errorMessages.length).toBeGreaterThan(0)
  })

  it('注册成功时应该导航到首页', async () => {
    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    vi.spyOn(store, 'register').mockResolvedValue({
      user: { id: '1', email: 'test@example.com', is_email_verified: false },
      token: 'test-token',
      refresh_token: 'test-refresh-token',
    })

    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('password123')
    await passwordInputs[1].setValue('password123')
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
    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'register').mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    )

    const wrapper = mount(RegisterForm)
    const form = wrapper.find('form')
    const submitButton = wrapper.find('button[type="submit"]')
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInputs = wrapper.findAll('input[type="password"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await passwordInputs[0].setValue('password123')
    await passwordInputs[1].setValue('password123')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(submitButton.attributes('disabled')).toBeDefined()
    expect(submitButton.text()).toBe('注册中...')
  })

  it('应该正确处理验证码更新事件', async () => {
    const wrapper = mount(RegisterForm)
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
    const wrapper = mount(RegisterForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    wrapper.vm.errors.captcha_answer = '验证码错误'

    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'new-captcha-id',
      captcha_answer: '5678',
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.errors.captcha_answer).toBe('')
  })
})
