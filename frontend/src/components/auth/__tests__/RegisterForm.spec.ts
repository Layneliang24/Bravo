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
})
