// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ResetPassword from '../ResetPasswordView.vue'
import ResetPasswordForm from '@/components/auth/ResetPasswordForm.vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Mock child components
vi.mock('@/components/auth/ResetPasswordForm.vue', () => ({
  default: {
    name: 'ResetPasswordForm',
    template: '<div class="reset-password-form-mock"></div>',
  },
}))

describe('ResetPasswordView.vue', () => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/reset-password', component: ResetPassword }],
  })

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should mount correctly and render the reset password form', async () => {
    const wrapper = mount(ResetPassword, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent(ResetPasswordForm).exists()).toBe(true)
  })
})
