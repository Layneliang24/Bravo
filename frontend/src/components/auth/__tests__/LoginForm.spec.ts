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
})
