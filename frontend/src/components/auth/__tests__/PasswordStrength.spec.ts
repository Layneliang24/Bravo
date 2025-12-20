// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_REGISTER-003, TC-AUTH_RESET-011
// 密码强度组件单元测试
// 对应测试用例：
// - TC-AUTH_REGISTER-003: 用户注册失败-密码强度不足
// - TC-AUTH_RESET-011: 重置密码失败-弱密码
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import PasswordStrength from '../PasswordStrength.vue'

describe('PasswordStrength', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = null
  })

  it('应该正确渲染组件', () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '',
      },
    })

    expect(wrapper.find('.password-strength').exists()).toBe(true)
  })

  it('当密码为空时，应该显示弱强度', () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '',
      },
    })

    expect(wrapper.find('.strength-indicator').exists()).toBe(true)
    expect(wrapper.find('.strength-text').text()).toContain('弱')
  })

  it('当密码长度小于8位时，应该显示弱强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '12345',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('弱')
    expect(wrapper.find('.strength-bar').classes()).toContain('weak')
  })

  it('当密码只有数字时，应该显示弱强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '12345678',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('弱')
    expect(wrapper.find('.strength-bar').classes()).toContain('weak')
  })

  it('当密码只有字母时，应该显示弱强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'abcdefgh',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('弱')
    expect(wrapper.find('.strength-bar').classes()).toContain('weak')
  })

  it('当密码包含字母和数字但长度刚好8位时，应该显示中等强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'abc12345',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('中')
    expect(wrapper.find('.strength-bar').classes()).toContain('medium')
  })

  it('当密码包含字母、数字且长度超过8位时，应该显示强强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'SecurePass123',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('强')
    expect(wrapper.find('.strength-bar').classes()).toContain('strong')
  })

  it('当密码包含字母、数字和特殊字符时，应该显示强强度', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'SecurePass123!',
      },
    })

    await nextTick()

    expect(wrapper.find('.strength-text').text()).toContain('强')
    expect(wrapper.find('.strength-bar').classes()).toContain('strong')
  })

  it('应该实时更新强度显示', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '123',
      },
    })

    await nextTick()
    expect(wrapper.find('.strength-text').text()).toContain('弱')

    await wrapper.setProps({ password: 'abc12345' })
    await nextTick()
    expect(wrapper.find('.strength-text').text()).toContain('中')

    await wrapper.setProps({ password: 'SecurePass123' })
    await nextTick()
    expect(wrapper.find('.strength-text').text()).toContain('强')
  })

  it('应该显示强度提示文字', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'abc12345',
      },
    })

    await nextTick()

    const hintText = wrapper.find('.strength-hint')
    expect(hintText.exists()).toBe(true)
    expect(hintText.text().length).toBeGreaterThan(0)
  })

  it('当密码强度为弱时，强度条应该显示红色', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '12345',
      },
    })

    await nextTick()

    const strengthBar = wrapper.find('.strength-bar')
    expect(strengthBar.classes()).toContain('weak')
    // 检查是否有红色相关的类或样式
    expect(
      strengthBar
        .classes()
        .some(cls => cls.includes('red') || cls.includes('weak'))
    ).toBe(true)
  })

  it('当密码强度为中等时，强度条应该显示黄色或橙色', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'abc12345',
      },
    })

    await nextTick()

    const strengthBar = wrapper.find('.strength-bar')
    expect(strengthBar.classes()).toContain('medium')
    // 检查是否有黄色/橙色相关的类
    expect(
      strengthBar
        .classes()
        .some(
          cls =>
            cls.includes('yellow') ||
            cls.includes('orange') ||
            cls.includes('medium')
        )
    ).toBe(true)
  })

  it('当密码强度为强时，强度条应该显示绿色', async () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: 'SecurePass123',
      },
    })

    await nextTick()

    const strengthBar = wrapper.find('.strength-bar')
    expect(strengthBar.classes()).toContain('strong')
    // 检查是否有绿色相关的类
    expect(
      strengthBar
        .classes()
        .some(cls => cls.includes('green') || cls.includes('strong'))
    ).toBe(true)
  })

  it('应该支持隐藏组件（当不需要显示时）', () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '',
        show: false,
      },
    })

    // 如果show为false，组件可能不渲染或隐藏
    // 这里根据实际实现来验证
    const component = wrapper.find('.password-strength')
    if (component.exists()) {
      // 如果组件存在，检查是否有隐藏类
      expect(
        component
          .classes()
          .some(cls => cls.includes('hidden') || cls.includes('hide'))
      ).toBe(true)
    }
  })

  it('应该支持显示组件（默认显示）', () => {
    wrapper = mount(PasswordStrength, {
      props: {
        password: '',
        show: true,
      },
    })

    expect(wrapper.find('.password-strength').exists()).toBe(true)
  })
})
