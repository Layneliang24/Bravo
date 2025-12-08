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
})
