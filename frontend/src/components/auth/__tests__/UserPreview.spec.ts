// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_PREVIEW-001, TC-AUTH_PREVIEW-002, TC-AUTH_PREVIEW-009, TC-AUTH_PREVIEW-010
// 用户预览组件单元测试
// 对应测试用例：
// - TC-AUTH_PREVIEW-001: 登录预验证成功返回头像信息
// - TC-AUTH_PREVIEW-002: 登录预验证成功-无头像返回默认
// - TC-AUTH_PREVIEW-009: 登录预览功能完整性测试
// - TC-AUTH_PREVIEW-010: 登录预览-输入账号密码后即可显示头像
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import UserPreview from '../UserPreview.vue'

describe('UserPreview', () => {
  beforeEach(() => {
    // 清理
  })

  it('应该正确渲染组件', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: 'https://example.com/avatar.jpg',
      },
    })

    expect(wrapper.find('.user-preview').exists()).toBe(true)
  })

  it('应该显示用户显示名称', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: null,
      },
    })

    expect(wrapper.text()).toContain('Test User')
  })

  it('应该显示真实头像', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: 'https://example.com/avatar.jpg',
      },
    })

    const avatar = wrapper.findComponent({ name: 'DefaultAvatar' })
    expect(avatar.exists()).toBe(true)
    expect(avatar.props('avatarUrl')).toBe('https://example.com/avatar.jpg')
  })

  it('应该显示默认头像（无头像时）', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: null,
        avatarLetter: 'T',
      },
    })

    const avatar = wrapper.findComponent({ name: 'DefaultAvatar' })
    expect(avatar.exists()).toBe(true)
    expect(avatar.props('avatarUrl')).toBeNull()
    expect(avatar.props('avatarLetter')).toBe('T')
  })

  it('应该支持加载中状态', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: null,
        loading: true,
      },
    })

    expect(wrapper.find('.loading').exists()).toBe(true)
  })

  it('无用户信息时应该不显示内容', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: null,
        avatarUrl: null,
        loading: false,
      },
    })

    expect(wrapper.find('.user-info').exists()).toBe(false)
    expect(wrapper.find('.loading').exists()).toBe(false)
  })

  it('应该正确传递avatarLetter给DefaultAvatar', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: null,
        avatarLetter: 'T',
      },
    })

    const avatar = wrapper.findComponent({ name: 'DefaultAvatar' })
    expect(avatar.props('avatarLetter')).toBe('T')
  })

  it('应该正确传递userName给DefaultAvatar', () => {
    const wrapper = mount(UserPreview, {
      props: {
        displayName: 'Test User',
        avatarUrl: null,
      },
    })

    const avatar = wrapper.findComponent({ name: 'DefaultAvatar' })
    expect(avatar.props('userName')).toBe('Test User')
  })
})
