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

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  },
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

// Clean up after each test
afterEach(() => {
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
