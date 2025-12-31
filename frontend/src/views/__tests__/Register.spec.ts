// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Register from '../Register.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Mock RegisterForm components to avoid deep mounting issues
vi.mock('@/components/auth/RegisterForm.vue', () => ({
  default: {
    name: 'RegisterForm',
    template: '<div class="register-form-mock"></div>',
  },
}))

describe('Register.vue', () => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/register', component: Register }],
  })

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should mount correctly and render the register form', async () => {
    const wrapper = mount(Register, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent(RegisterForm).exists()).toBe(true)
  })
})
