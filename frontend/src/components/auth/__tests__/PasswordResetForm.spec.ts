// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_RESET-001, TC-AUTH_RESET-002, TC-AUTH_RESET-007, TC-AUTH_RESET-008
// 密码重置邮件发送表单功能单元测试
// 对应测试用例：
// - TC-AUTH_RESET-001: 发送密码重置邮件
// - TC-AUTH_RESET-002: 发送密码重置邮件-需要验证码
// - TC-AUTH_RESET-007: 发送密码重置邮件-邮箱不存在
// - TC-AUTH_RESET-008: 发送密码重置邮件-验证码错误
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useRouter } from 'vue-router'
import PasswordResetForm from '../PasswordResetForm.vue'
import { useAuthStore } from '@/stores/auth'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
}))

describe('PasswordResetForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)
  })

  it('应该正确渲染密码重置表单', () => {
    const wrapper = mount(PasswordResetForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('应该包含邮箱输入框', () => {
    const wrapper = mount(PasswordResetForm)
    const emailInput = wrapper.find('input[type="email"]')

    expect(emailInput.exists()).toBe(true)
  })

  it('应该包含验证码组件', () => {
    const wrapper = mount(PasswordResetForm)
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    expect(captchaComponent.exists()).toBe(true)
  })

  it('应该包含提交按钮', () => {
    const wrapper = mount(PasswordResetForm)
    const submitButton = wrapper.find('button[type="submit"]')

    expect(submitButton.exists()).toBe(true)
  })

  it('应该验证邮箱格式', async () => {
    const wrapper = mount(PasswordResetForm)
    const form = wrapper.find('form')
    const emailInput = wrapper.find('input[type="email"]')

    await emailInput.setValue('invalid-email')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('提交成功时应该调用auth store的sendPasswordReset方法', async () => {
    const authStore = useAuthStore()
    const sendPasswordResetSpy = vi
      .spyOn(authStore, 'sendPasswordReset')
      .mockResolvedValue({ message: '密码重置邮件已发送，请查收' })

    const wrapper = mount(PasswordResetForm)

    const emailInput = wrapper.find('input[type="email"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(sendPasswordResetSpy).toHaveBeenCalledWith({
      email: 'test@example.com',
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
  })

  it('提交失败时应该显示错误信息', async () => {
    const authStore = useAuthStore()
    vi.spyOn(authStore, 'sendPasswordReset').mockRejectedValue(
      new Error('验证码错误')
    )

    const wrapper = mount(PasswordResetForm)

    const emailInput = wrapper.find('input[type="email"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'invalid-captcha-id',
      captcha_answer: 'wrong',
    })
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('提交时应该禁用提交按钮', async () => {
    const authStore = useAuthStore()
    vi.spyOn(authStore, 'sendPasswordReset').mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(() => resolve({ message: '成功' }), 100)
        )
    )

    const wrapper = mount(PasswordResetForm)

    const emailInput = wrapper.find('input[type="email"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })
    const submitButton = wrapper.find('button[type="submit"]')

    await emailInput.setValue('test@example.com')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  it('提交成功后应该显示成功消息', async () => {
    const authStore = useAuthStore()
    vi.spyOn(authStore, 'sendPasswordReset').mockResolvedValue({
      message: '密码重置邮件已发送，请查收',
    })

    const wrapper = mount(PasswordResetForm)

    const emailInput = wrapper.find('input[type="email"]')
    const captchaComponent = wrapper.findComponent({ name: 'Captcha' })

    await emailInput.setValue('test@example.com')
    await captchaComponent.vm.$emit('captcha-update', {
      captcha_id: 'test-captcha-id',
      captcha_answer: '1234',
    })
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const successMessage = wrapper.find('.success-message')
    expect(successMessage.exists()).toBe(true)
    expect(successMessage.text()).toContain('密码重置邮件已发送')
  })
})
