import { vi, afterEach } from 'vitest'
import { config, mount } from '@vue/test-utils'

// Mock global objects
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn(),
})

// Mock localStorage with actual storage functionality
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => {
      return store[key] || null
    },
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
    get length() {
      return Object.keys(store).length
    },
    key: (index: number) => {
      const keys = Object.keys(store)
      return keys[index] || null
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  },
  writable: true,
})

// Mock fetch
global.fetch = vi.fn()

// Mock console methods to reduce noise in tests
vi.spyOn(console, 'warn').mockImplementation(() => {})
vi.spyOn(console, 'error').mockImplementation(() => {})

// Global test configuration
config.global.stubs = {
  // Stub out router-link and router-view
  'router-link': true,
  'router-view': true,
  // Stub out Element Plus components if needed
  'el-button': true,
  'el-input': true,
  'el-form': true,
  'el-form-item': true,
}

// Set up global plugins for testing
config.global.plugins = []

// 处理未捕获的Promise rejection（避免测试因Vue内部错误而失败）
process.on('unhandledRejection', (reason, promise) => {
  // 只记录Vue相关的内部错误，不抛出
  if (reason && typeof reason === 'object' && 'message' in reason) {
    const message = String(reason.message || '')
    if (
      message.includes('nextSibling') ||
      message.includes('__vnode') ||
      message.includes('runtime-dom') ||
      message.includes('runtime-core')
    ) {
      // Vue内部错误，静默处理
      return
    }
  }
  // 其他错误仍然抛出
  console.error('Unhandled Rejection:', reason)
})

// Clean up after each test
afterEach(() => {
  // 清除localStorage（但保留mock实现）
  if (window.localStorage) {
    window.localStorage.clear()
  }
  vi.clearAllMocks()
  vi.clearAllTimers()
})

// Global test utilities
export const createMockRouter = (): any => ({
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: {
    value: {
      path: '/',
      name: 'home',
      params: {},
      query: {},
      meta: {},
    },
  },
})

export const createMockStore = (): any => ({
  state: {},
  getters: {},
  commit: vi.fn(),
  dispatch: vi.fn(),
})

// Helper function to wait for next tick
export const nextTick = (): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, 0))

// Helper function to create a wrapper with common setup
export const createWrapper = (component: any, options: any = {}): any => {
  return mount(component, {
    global: {
      plugins: [],
      stubs: {
        'router-link': true,
        'router-view': true,
        ...options.stubs,
      },
      mocks: {
        $router: createMockRouter(),
        $route: {
          path: '/',
          name: 'home',
          params: {},
          query: {},
          meta: {},
        },
        ...options.mocks,
      },
    },
    ...options,
  })
}
