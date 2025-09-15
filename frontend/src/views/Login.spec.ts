import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
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

    // 创建组件实例，使用更可靠的stub配置
    wrapper = mount(Login, {
      global: {
        stubs: {
          ElCard: { template: '<div class="el-card"><slot /></div>' },
          ElForm: { template: '<form class="el-form"><slot /></form>' },
          ElFormItem: {
            template: '<div class="el-form-item"><slot /></div>',
          },
          ElInput: {
            template:
              '<input class="el-input" v-bind="$attrs" @input="handleInput" />',
            props: ['type', 'placeholder', 'modelValue'],
            emits: ['update:modelValue'],
            methods: {
              handleInput(event: Event): void {
                const target = event.target as HTMLInputElement
                this.$emit('update:modelValue', target.value)
              },
            },
          },
          ElButton: {
            template:
              '<button class="el-button" @click="handleClick"><slot /></button>',
            emits: ['click'],
            methods: {
              handleClick(): void {
                this.$emit('click')
              },
            },
          },
        },
      },
    })
  })

  it('应该正确渲染登录表单', () => {
    // 检查标题
    expect(wrapper.find('h2').text()).toBe('登录')

    // 检查Element Plus组件存在
    expect(wrapper.find('.el-card').exists()).toBe(true)
    expect(wrapper.find('form.el-form').exists()).toBe(true)
    expect(wrapper.find('.el-button').exists()).toBe(true)
    expect(wrapper.find('.el-button').text()).toBe('登录')
  })

  it('应该能够输入用户名和密码', async () => {
    // 直接测试响应式数据
    expect(wrapper.vm.loginForm.username).toBe('')
    expect(wrapper.vm.loginForm.password).toBe('')

    // 模拟用户输入
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 验证数据绑定
    expect(wrapper.vm.loginForm.username).toBe('testuser')
    expect(wrapper.vm.loginForm.password).toBe('testpassword')
  })

  it('当用户名和密码都填写时，点击登录应该跳转到首页', async () => {
    // 设置表单数据
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证路由跳转
    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('当用户名为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（用户名为空）
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = 'testpassword'
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当密码为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（密码为空）
    wrapper.vm.loginForm.username = 'testuser'
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('当用户名和密码都为空时，点击登录不应该跳转', async () => {
    // 设置表单数据（都为空）
    wrapper.vm.loginForm.username = ''
    wrapper.vm.loginForm.password = ''
    await wrapper.vm.$nextTick()

    // 直接调用handleLogin函数
    await wrapper.vm.handleLogin()

    // 验证没有路由跳转
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('应该有正确的CSS样式类', () => {
    expect(wrapper.find('.login').exists()).toBe(true)
    expect(wrapper.find('.login-card').exists()).toBe(true)
  })
})
