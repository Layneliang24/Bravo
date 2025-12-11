// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import Login from '../Login.vue'

describe('Login - Glassmorphism Design', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该正确渲染登录页面', () => {
    const wrapper = mount(Login)

    expect(wrapper.find('.login-view').exists()).toBe(true)
    expect(wrapper.find('.login-container').exists()).toBe(true)
  })

  it('应该包含背景图片区域', () => {
    const wrapper = mount(Login)

    expect(wrapper.find('.background-image').exists()).toBe(true)
  })

  it('应该包含玻璃态卡片容器', () => {
    const wrapper = mount(Login)

    expect(wrapper.find('.glass-card').exists()).toBe(true)
  })

  it('应该显示主标题 "Login"', () => {
    const wrapper = mount(Login)

    const title = wrapper.find('.main-title')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Login')
  })

  it('应该显示副标题 "Welcome onboard with us!"', () => {
    const wrapper = mount(Login)

    const subtitle = wrapper.find('.subtitle')
    expect(subtitle.exists()).toBe(true)
    expect(subtitle.text()).toBe('Welcome onboard with us!')
  })

  it('应该包含 LoginForm 组件', () => {
    const wrapper = mount(Login)

    const loginForm = wrapper.findComponent({ name: 'LoginForm' })
    expect(loginForm.exists()).toBe(true)
  })

  it('应该包含装饰性椭圆元素', () => {
    const wrapper = mount(Login)

    const ellipses = wrapper.findAll('.decorative-ellipse')
    expect(ellipses.length).toBeGreaterThan(0)
  })
})
