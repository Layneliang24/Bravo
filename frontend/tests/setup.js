// Vue Test Utils 测试配置 - 在测试框架初始化后运行
import { config } from '@vue/test-utils'

// Vue Test Utils 全局配置
config.global.mocks = {
  $t: key => key, // i18n mock
  $route: {
    path: '/',
    params: {},
    query: {},
  },
  $router: {
    push: jest.fn(),
    replace: jest.fn(),
    go: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
  },
}

// 全局插件配置
config.global.plugins = []

// 控制台警告过滤
const originalWarn = console.warn
console.warn = (...args) => {
  // 过滤掉一些已知的无害警告
  const message = args[0]
  if (
    typeof message === 'string' &&
    (message.includes('[Vue warn]') ||
      message.includes('Download the Vue Devtools'))
  ) {
    return
  }
  originalWarn.apply(console, args)
}
