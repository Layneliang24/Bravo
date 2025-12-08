// REQ-ID: REQ-2025-003-user-login
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useRouter, useRoute } from 'vue-router'
import VerifyEmailView from '../VerifyEmailView.vue'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
  useRoute: vi.fn(),
}))

describe('VerifyEmailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)
  })

  it('应该正确渲染邮箱验证页面', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(VerifyEmailView)

    expect(wrapper.find('.verify-email-view').exists()).toBe(true)
  })

  it('应该从URL中获取token参数', () => {
    const mockRoute = {
      query: { token: 'test-verify-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(VerifyEmailView)

    expect(wrapper.vm.token).toBe('test-verify-token')
  })

  it('没有token时应该显示错误消息', () => {
    const mockRoute = {
      query: {},
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(VerifyEmailView)

    expect(wrapper.text()).toContain('无效的验证链接')
  })

  it('挂载时应该自动调用verifyEmail action', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    const verifyEmailSpy = vi
      .spyOn(store, 'verifyEmail')
      .mockResolvedValue({ message: '邮箱验证成功' })

    mount(VerifyEmailView)
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(verifyEmailSpy).toHaveBeenCalledWith('test-token')
  })

  it('验证成功时应该显示成功消息', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'verifyEmail').mockResolvedValue({
      message: '邮箱验证成功',
    })

    const wrapper = mount(VerifyEmailView)
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('邮箱验证成功')
    const successMessage = wrapper.find('.verification-success')
    expect(successMessage.exists()).toBe(true)
  })

  it('验证失败时应该显示错误消息', async () => {
    const mockRoute = {
      query: { token: 'invalid-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'verifyEmail').mockRejectedValue(
      new Error('验证链接已过期或无效')
    )

    const wrapper = mount(VerifyEmailView)
    await new Promise(resolve => setTimeout(resolve, 200))

    const errorMessage = wrapper.find('.verification-error')
    expect(errorMessage.exists()).toBe(true)
    expect(wrapper.text()).toContain('验证链接已过期或无效')
  })

  it('验证中应该显示加载状态', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'verifyEmail').mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    )

    const wrapper = mount(VerifyEmailView)
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('验证中')
  })

  it('验证成功后应该提供跳转到登录页的按钮', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'verifyEmail').mockResolvedValue({
      message: '邮箱验证成功',
    })

    const wrapper = mount(VerifyEmailView)
    await new Promise(resolve => setTimeout(resolve, 200))

    const loginButton = wrapper.find('.login-button')
    expect(loginButton.exists()).toBe(true)

    await loginButton.trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/login')
  })

  it('验证失败后应该提供重新发送验证邮件的选项', async () => {
    const mockRoute = {
      query: { token: 'invalid-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const { useAuthStore } = await import('@/stores/auth')
    const store = useAuthStore()
    vi.spyOn(store, 'verifyEmail').mockRejectedValue(
      new Error('验证链接已过期')
    )

    const wrapper = mount(VerifyEmailView)
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('重新发送')
  })
})
