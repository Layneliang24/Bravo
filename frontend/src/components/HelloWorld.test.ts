import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

// 简单的测试组件
const helloWorld = {
  name: 'HelloWorld',
  props: {
    msg: String,
  },
  template: '<h1>{{ msg }}</h1>',
}

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(helloWorld, { props: { msg: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })

  it('should be a Vue component', () => {
    expect(helloWorld.name).toBe('HelloWorld')
  })

  it('should have msg prop', () => {
    expect(helloWorld.props).toHaveProperty('msg')
  })
})
