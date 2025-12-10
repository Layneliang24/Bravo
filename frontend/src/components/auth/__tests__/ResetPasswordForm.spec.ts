// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useRouter, useRoute } from 'vue-router'
import ResetPasswordForm from '../ResetPasswordForm.vue'
import { useAuthStore } from '@/stores/auth'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(),
  useRoute: vi.fn(),
}))

describe('ResetPasswordForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)
  })

  it('应该正确渲染重置密码表单', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.findAll('input[type="password"]').length).toBe(2)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('应该从URL中获取token参数', () => {
    const mockRoute = {
      query: { token: 'test-reset-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)

    expect(wrapper.vm.token).toBe('test-reset-token')
  })

  it('应该包含新密码输入框', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    expect(passwordInputs.length).toBeGreaterThanOrEqual(1)
  })

  it('应该包含确认密码输入框', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    expect(passwordInputs.length).toBe(2)
  })

  it('应该包含密码强度组件', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const passwordStrengthComponent = wrapper.findComponent({
      name: 'PasswordStrength',
    })

    expect(passwordStrengthComponent.exists()).toBe(true)
  })

  it('应该包含提交按钮', () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const submitButton = wrapper.find('button[type="submit"]')

    expect(submitButton.exists()).toBe(true)
  })

  it('应该验证密码长度', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const form = wrapper.find('form')
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('short')
    await passwordInputs[1].setValue('short')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('应该验证密码是否匹配', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)
    const form = wrapper.find('form')
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('Password123!')
    await passwordInputs[1].setValue('DifferentPassword123!')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('提交成功时应该调用auth store的resetPassword方法', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const authStore = useAuthStore()
    const resetPasswordSpy = vi
      .spyOn(authStore, 'resetPassword')
      .mockResolvedValue({ message: '密码重置成功' })

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('NewPassword123!')
    await passwordInputs[1].setValue('NewPassword123!')
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(resetPasswordSpy).toHaveBeenCalledWith({
      token: 'test-token',
      password: 'NewPassword123!',
      password_confirm: 'NewPassword123!',
    })
  })

  it('提交失败时应该显示错误信息', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const authStore = useAuthStore()
    vi.spyOn(authStore, 'resetPassword').mockRejectedValue(
      new Error('无效的重置链接')
    )

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('NewPassword123!')
    await passwordInputs[1].setValue('NewPassword123!')
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
  })

  it('提交时应该禁用提交按钮', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const authStore = useAuthStore()
    vi.spyOn(authStore, 'resetPassword').mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(() => resolve({ message: '成功' }), 100)
        )
    )

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')
    const submitButton = wrapper.find('button[type="submit"]')

    await passwordInputs[0].setValue('NewPassword123!')
    await passwordInputs[1].setValue('NewPassword123!')
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  it('提交成功后应该显示成功消息并跳转', async () => {
    const mockRoute = {
      query: { token: 'test-token' },
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const routerPush = vi.fn()
    const mockRouter = { push: routerPush }
    ;(useRouter as any).mockReturnValue(mockRouter)

    const authStore = useAuthStore()
    vi.spyOn(authStore, 'resetPassword').mockResolvedValue({
      message: '密码重置成功',
    })

    const wrapper = mount(ResetPasswordForm)
    const passwordInputs = wrapper.findAll('input[type="password"]')

    await passwordInputs[0].setValue('NewPassword123!')
    await passwordInputs[1].setValue('NewPassword123!')
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const successMessage = wrapper.find('.success-message')
    expect(successMessage.exists()).toBe(true)
    expect(successMessage.text()).toContain('密码重置成功')
  })

  it('无token参数时应该显示错误', () => {
    const mockRoute = {
      query: {},
    }
    ;(useRoute as any).mockReturnValue(mockRoute)

    const wrapper = mount(ResetPasswordForm)

    const errorMessage = wrapper.find('.error-message')
    expect(errorMessage.exists()).toBe(true)
    expect(errorMessage.text()).toContain('无效')
  })
})
