// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ForgotPassword from '../ForgotPasswordView.vue'
import PasswordResetForm from '@/components/auth/PasswordResetForm.vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Mock child components
vi.mock('@/components/auth/PasswordResetForm.vue', () => ({
  default: {
    name: 'PasswordResetForm',
    template: '<div class="password-reset-form-mock"></div>',
  },
}))

describe('ForgotPasswordView.vue', () => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/forgot-password', component: ForgotPassword }],
  })

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should mount correctly and render the password reset form', async () => {
    const wrapper = mount(ForgotPassword, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent(PasswordResetForm).exists()).toBe(true)
  })
})
