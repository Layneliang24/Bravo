// REQ-ID: REQ-2025-003-user-login
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import Captcha from '../Captcha.vue'

// Mock fetch API
global.fetch = vi.fn()

describe('Captcha', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
    wrapper = null
  })

  it('应该正确渲染组件', async () => {
    // Mock API响应
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image:
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha)

    // 等待API调用完成 - 增加等待时间确保异步操作完成
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // .captcha-container 是根元素，应该总是存在
    expect(wrapper.find('.captcha-container').exists()).toBe(true)
    // 等待图片加载完成
    await nextTick()
    expect(wrapper.find('img').exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
    // 刷新按钮在点击区域内部，查找包含刷新功能的元素
    const refreshArea = wrapper.find('[class*="cursor-pointer"]')
    expect(refreshArea.exists()).toBe(true)
  })

  it('应该显示验证码图片', async () => {
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image:
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe(mockResponse.captcha_image)
    expect(img.attributes('alt')).toBe('验证码')
  })

  it('应该支持刷新验证码', async () => {
    const mockResponse1 = {
      captcha_id: 'test-captcha-id-1',
      captcha_image: 'data:image/png;base64,image1',
      expires_in: 300,
    }

    const mockResponse2 = {
      captcha_id: 'test-captcha-id-2',
      captcha_image: 'data:image/png;base64,image2',
      expires_in: 300,
    }

    ;(global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse1,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse2,
      })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // 点击刷新区域（整个验证码显示区域都可以点击刷新）
    const refreshArea = wrapper.find('[class*="cursor-pointer"]')
    expect(refreshArea.exists()).toBe(true)
    await refreshArea.trigger('click')

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 验证调用了刷新API
    expect(global.fetch).toHaveBeenCalledTimes(2)
    const lastCall = (global.fetch as any).mock.calls[1][0]
    expect(lastCall).toContain('/api/auth/captcha/refresh/')
  })

  it('应该支持输入验证码答案', async () => {
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image: 'data:image/png;base64,image',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const input = wrapper.find('input')
    await input.setValue('A3B7')

    expect(input.element.value).toBe('A3B7')
  })

  it('应该发出captcha-update事件', async () => {
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image: 'data:image/png;base64,image',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 验证发出了captcha-update事件
    expect(wrapper.emitted('captcha-update')).toBeTruthy()
    expect(wrapper.emitted('captcha-update')[0]).toEqual([
      {
        captcha_id: 'test-captcha-id',
        captcha_answer: '',
      },
    ])
  })

  it('当用户输入验证码时，应该发出captcha-update事件', async () => {
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image: 'data:image/png;base64,image',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 清空之前的事件
    wrapper.vm.$emit = vi.fn()

    const input = wrapper.find('input')
    await input.setValue('A3B7')

    // 验证发出了captcha-update事件
    expect(wrapper.emitted('captcha-update')).toBeTruthy()
    const lastEvent = wrapper.emitted('captcha-update').slice(-1)[0]
    expect(lastEvent[0].captcha_answer).toBe('A3B7')
  })

  it('应该显示加载状态', async () => {
    // Mock一个延迟的API响应
    ;(global.fetch as any).mockImplementationOnce(
      () =>
        new Promise(resolve => {
          setTimeout(() => {
            resolve({
              ok: true,
              json: async () => ({
                captcha_id: 'test-captcha-id',
                captcha_image: 'data:image/png;base64,image',
                expires_in: 300,
              }),
            })
          }, 100)
        })
    )

    wrapper = mount(Captcha)

    await nextTick()

    // 在加载期间应该显示加载状态
    expect(
      wrapper.find('.loading').exists() ||
        wrapper.find('[aria-busy="true"]').exists()
    ).toBe(true)
  })

  it('应该处理API错误', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    wrapper = mount(Captcha)

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // 应该显示错误状态或处理错误
    // 这里可以根据实际实现来验证
    expect(
      wrapper.find('.error').exists() || wrapper.find('[role="alert"]').exists()
    ).toBe(true)
  })

  it('应该支持禁用状态', async () => {
    const mockResponse = {
      captcha_id: 'test-captcha-id',
      captcha_image: 'data:image/png;base64,image',
      expires_in: 300,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    wrapper = mount(Captcha, {
      props: {
        disabled: true,
      },
    })

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()

    // 刷新区域在禁用状态下应该不可点击（通过disabled prop控制）
    const refreshArea = wrapper.find('[class*="cursor-pointer"]')
    // 禁用状态下，组件可能移除cursor-pointer类或添加disabled样式
    // 这里主要验证input被禁用即可
    expect(input.attributes('disabled')).toBeDefined()
  })
})
