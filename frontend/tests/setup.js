// 全局测试环境设置
import { config } from '@vue/test-utils';

// Vue Test Utils 全局配置
config.global.mocks = {
  $t: (key) => key, // i18n mock
  $route: {
    path: '/',
    params: {},
    query: {}
  },
  $router: {
    push: jest.fn(),
    replace: jest.fn(),
    go: jest.fn(),
    back: jest.fn(),
    forward: jest.fn()
  }
};

// 全局插件配置
config.global.plugins = [];

// DOM 环境设置
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// IntersectionObserver mock
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// ResizeObserver mock
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// 本地存储 mock
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// 会话存储 mock
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Fetch mock
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  })
);

// 控制台警告过滤
const originalWarn = console.warn;
console.warn = (...args) => {
  // 过滤掉一些已知的无害警告
  const message = args[0];
  if (
    typeof message === 'string' &&
    (
      message.includes('[Vue warn]') ||
      message.includes('Download the Vue Devtools')
    )
  ) {
    return;
  }
  originalWarn.apply(console, args);
};

// 错误处理
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// 测试环境标识
process.env.NODE_ENV = 'test';
process.env.VUE_APP_ENV = 'test';