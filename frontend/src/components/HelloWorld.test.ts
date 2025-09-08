import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createApp } from 'vue'

// 简单的测试组件
const HelloWorld = {
  name: 'HelloWorld',
  props: {
    msg: String
  },
  template: '<h1>{{ msg }}</h1>'
}

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })

  it('should be a Vue component', () => {
    expect(HelloWorld.name).toBe('HelloWorld')
  })

  it('should have msg prop', () => {
    expect(HelloWorld.props).toHaveProperty('msg')
  })
})