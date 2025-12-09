// REQ-ID: REQ-2025-003-user-login
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Login from './Login.vue'

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', async () => {
  const actual = (await vi.importActual('vue-router')) as Record<
    string,
    unknown
  >
  return {
    ...actual,
    useRouter: (): { push: typeof mockPush } => ({
      push: mockPush,
    }),
  }
})

describe('Login.vue', () => {
  let wrapper: any

  beforeEach(() => {
    // 清除所有mock调用记录
    vi.clearAllMocks()

    // 设置Pinia
    setActivePinia(createPinia())

    // 创建组件实例
    wrapper = mount(Login, {
      global: {
        stubs: {
          LoginForm: {
            template: '<div class="login-form-stub">LoginForm</div>',
          },
        },
      },
    })
  })

  it('应该正确渲染登录表单', () => {
    // 检查标题
    expect(wrapper.find('.login-title').text()).toBe('欢迎回来')

    // 检查LoginForm组件存在
    expect(wrapper.find('.login-form-stub').exists()).toBe(true)

    // 检查容器类
    expect(wrapper.find('.login-view').exists()).toBe(true)
    expect(wrapper.find('.login-container').exists()).toBe(true)
  })

  it('应该包含移动端布局', () => {
    const mobileLayout = wrapper.find('.mobile-layout')
    expect(mobileLayout.exists()).toBe(true)
    expect(mobileLayout.find('.login-form-wrapper').exists()).toBe(true)
  })

  it('应该包含桌面端布局', () => {
    const desktopLayout = wrapper.find('.desktop-layout')
    expect(desktopLayout.exists()).toBe(true)
    expect(desktopLayout.find('.brand-section').exists()).toBe(true)
    expect(desktopLayout.find('.form-section').exists()).toBe(true)
  })

  it('应该包含品牌展示区域', () => {
    const brandSection = wrapper.find('.brand-section')
    expect(brandSection.exists()).toBe(true)
    expect(brandSection.find('.brand-title').text()).toBe('Bravo')
    expect(brandSection.find('.brand-subtitle').text()).toBe('您的智能工作伙伴')
  })

  it('应该包含品牌特性列表', () => {
    const featureItems = wrapper.findAll('.feature-item')
    expect(featureItems.length).toBe(3)
    expect(featureItems[0].find('.feature-text').text()).toBe('安全可靠')
    expect(featureItems[1].find('.feature-text').text()).toBe('快速高效')
    expect(featureItems[2].find('.feature-text').text()).toBe('智能便捷')
  })

  it('应该有正确的CSS样式类', () => {
    expect(wrapper.find('.login-view').exists()).toBe(true)
    expect(wrapper.find('.login-container').exists()).toBe(true)
    expect(wrapper.find('.login-form-wrapper').exists()).toBe(true)
  })
})
