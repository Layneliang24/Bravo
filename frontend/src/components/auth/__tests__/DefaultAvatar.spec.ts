// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_PREVIEW-002
// 默认头像组件单元测试
// 对应测试用例：
// - TC-AUTH_PREVIEW-002: 登录预验证成功-无头像返回默认
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DefaultAvatar from '../DefaultAvatar.vue'

describe('DefaultAvatar', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = null
  })

  it('应该正确渲染组件', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'A',
      },
    })

    expect(wrapper.find('.default-avatar').exists()).toBe(true)
  })

  it('当有avatar_url时，应该显示真实头像', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: 'https://example.com/avatar.jpg',
        avatarLetter: 'A',
      },
    })

    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/avatar.jpg')
    expect(img.attributes('alt')).toBeDefined()
  })

  it('当没有avatar_url时，应该显示首字母生成的默认头像', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'T',
      },
    })

    // 不应该有img标签
    expect(wrapper.find('img').exists()).toBe(false)

    // 应该有显示首字母的元素
    const letterElement = wrapper.find('.avatar-letter')
    expect(letterElement.exists()).toBe(true)
    expect(letterElement.text()).toBe('T')
  })

  it('当avatar_url为空字符串时，应该显示默认头像', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: '',
        avatarLetter: 'B',
      },
    })

    expect(wrapper.find('img').exists()).toBe(false)
    const letterElement = wrapper.find('.avatar-letter')
    expect(letterElement.exists()).toBe(true)
    expect(letterElement.text()).toBe('B')
  })

  it('应该支持不同尺寸', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'A',
        size: 'large',
      },
    })

    expect(wrapper.find('.default-avatar').classes()).toContain('size-large')
  })

  it('应该支持自定义类名', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'A',
      },
      attrs: {
        class: 'custom-class',
      },
    })

    expect(wrapper.find('.default-avatar').classes()).toContain('custom-class')
  })

  it('当头像加载失败时，应该回退到默认头像', async () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: 'https://example.com/invalid-avatar.jpg',
        avatarLetter: 'C',
      },
    })

    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)

    // 模拟图片加载失败
    await img.trigger('error')
    await wrapper.vm.$nextTick()

    // 应该回退到显示首字母
    expect(wrapper.find('img').exists()).toBe(false)
    const letterElement = wrapper.find('.avatar-letter')
    expect(letterElement.exists()).toBe(true)
    expect(letterElement.text()).toBe('C')
  })

  it('应该正确显示单字符首字母', () => {
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'Z',
      },
    })

    const letterElement = wrapper.find('.avatar-letter')
    expect(letterElement.text()).toBe('Z')
  })

  it('应该支持圆形和方形两种形状', () => {
    // 测试圆形（默认）
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'A',
        shape: 'circle',
      },
    })

    expect(wrapper.find('.default-avatar').classes()).toContain('shape-circle')

    // 测试方形
    wrapper = mount(DefaultAvatar, {
      props: {
        avatarUrl: null,
        avatarLetter: 'A',
        shape: 'square',
      },
    })

    expect(wrapper.find('.default-avatar').classes()).toContain('shape-square')
  })
})
