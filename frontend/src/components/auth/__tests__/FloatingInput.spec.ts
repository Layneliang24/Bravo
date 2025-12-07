import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FloatingInput from '../FloatingInput.vue'

describe('FloatingInput', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = null
  })

  it('应该正确渲染输入框', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
      },
    })

    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('label').exists()).toBe(true)
    expect(wrapper.find('label').text()).toBe('邮箱')
  })

  it('当输入框有值时，标签应该上浮', async () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
      },
    })

    // 初始状态：标签应该在输入框内
    const label = wrapper.find('label')
    expect(label.classes()).toContain('floating-label')

    // 输入值后，标签应该上浮
    await wrapper.setProps({ modelValue: 'test@example.com' })
    await wrapper.vm.$nextTick()

    expect(label.classes()).toContain('floating-label-active')
  })

  it('当输入框聚焦时，标签应该上浮', async () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
      },
    })

    const input = wrapper.find('input')
    const label = wrapper.find('label')

    // 聚焦输入框
    await input.trigger('focus')
    await wrapper.vm.$nextTick()

    expect(label.classes()).toContain('floating-label-active')
  })

  it('应该显示错误状态', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
        error: '邮箱格式不正确',
      },
    })

    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toBe('邮箱格式不正确')
    expect(wrapper.find('input').classes()).toContain('error')
  })

  it('应该支持图标显示', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
        icon: 'user',
      },
    })

    expect(wrapper.find('.input-icon').exists()).toBe(true)
  })

  it('应该支持不同类型的输入', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '密码',
        modelValue: '',
        type: 'password',
      },
    })

    expect(wrapper.find('input').attributes('type')).toBe('password')
  })

  it('应该正确触发input事件', async () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
      },
    })

    const input = wrapper.find('input')
    await input.setValue('test@example.com')
    await input.trigger('input')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([
      'test@example.com',
    ])
  })

  it('应该支持禁用状态', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
        disabled: true,
      },
    })

    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('应该支持占位符', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
        placeholder: '请输入邮箱地址',
      },
    })

    expect(wrapper.find('input').attributes('placeholder')).toBe(
      '请输入邮箱地址'
    )
  })

  it('应该支持必填标记', () => {
    wrapper = mount(FloatingInput, {
      props: {
        label: '邮箱',
        modelValue: '',
        required: true,
      },
    })

    expect(wrapper.find('label').text()).toContain('*')
  })
})
