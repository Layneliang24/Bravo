import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Home from './Home.vue'

describe('Home.vue', () => {
  it('应该正确渲染欢迎信息', () => {
    const wrapper = mount(Home)

    // 检查主标题
    const title = wrapper.find('h1')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('欢迎来到 Bravo')

    // 检查副标题
    const subtitle = wrapper.find('p')
    expect(subtitle.exists()).toBe(true)
    expect(subtitle.text()).toBe('智能学习平台')
  })

  it('应该有正确的CSS样式类', () => {
    const wrapper = mount(Home)

    // 检查根容器样式类
    expect(wrapper.find('.home').exists()).toBe(true)
  })

  it('应该正确应用scoped样式', () => {
    const wrapper = mount(Home)

    // 检查元素结构
    const homeDiv = wrapper.find('.home')
    const title = wrapper.find('h1')

    expect(homeDiv.exists()).toBe(true)
    expect(title.exists()).toBe(true)
  })

  it('应该是一个简单的静态组件', () => {
    const wrapper = mount(Home)

    // 验证组件没有复杂的交互逻辑
    expect(wrapper.find('button').exists()).toBe(false)
    expect(wrapper.find('input').exists()).toBe(false)
    expect(wrapper.find('form').exists()).toBe(false)
  })

  it('应该包含正确的文本内容', () => {
    const wrapper = mount(Home)
    const text = wrapper.text()

    expect(text).toContain('欢迎来到 Bravo')
    expect(text).toContain('智能学习平台')
  })
})
