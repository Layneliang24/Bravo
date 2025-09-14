module.exports = {
  // 基础配置
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/*.(test|spec).{js,jsx,ts,tsx}',
  ],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    '^.+\\.vue$': '@vue/vue3-jest',
  },
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'vue', 'json'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },

  // 功能映射配置
  setupFilesAfterEnv: [
    '<rootDir>/../matchFeatures.js',
    '<rootDir>/tests/coverage-setup.js',
  ],

  // 覆盖率配置
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx,vue}',
    '!src/**/*.d.ts',
    '!src/main.{js,ts}',
    '!src/registerServiceWorker.{js,ts}',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
    '!src/**/node_modules/**',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'text-lcov',
    'html',
    'json',
    'json-summary',
    'clover',
  ],

  // 严格的覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90,
    },
    // 关键组件更高要求
    './src/components/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95,
    },
    './src/views/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85,
    },
    './src/utils/': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
  },

  // 测试报告配置
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'coverage',
        outputName: 'junit.xml',
        ancestorSeparator: ' › ',
        uniqueOutputName: 'false',
        suiteNameTemplate: '{filepath}',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
      },
    ],
    [
      'jest-html-reporters',
      {
        publicPath: 'coverage/html-report',
        filename: 'report.html',
        expand: true,
        hideIcon: false,
        pageTitle: 'Frontend Test Report',
      },
    ],
  ],

  // CI环境配置
  ci: process.env.CI === 'true',
  verbose: process.env.CI === 'true',
  bail: process.env.CI === 'true' ? 1 : false,

  // 全局变量
  globals: {
    'vue-jest': {
      pug: {
        doctype: 'html',
      },
    },
    // 功能映射环境变量
    VALIDATE_FEATURE_COVERAGE: process.env.VALIDATE_FEATURE_COVERAGE || 'true',
    ENFORCE_FEATURE_MAPPING: process.env.ENFORCE_FEATURE_MAPPING || 'true',
  },

  // 测试超时
  testTimeout: 10000,

  // 清理配置
  clearMocks: true,
  restoreMocks: true,

  // 忽略模式
  testPathIgnorePatterns: ['/node_modules/', '/dist/', '/build/'],

  // 监听模式配置
  watchPathIgnorePatterns: ['/node_modules/', '/coverage/', '/dist/'],

  // 错误处理
  errorOnDeprecated: true,

  // 快照配置
  snapshotSerializers: ['jest-serializer-vue'],

  // 模块解析
  resolver: undefined,

  // 自定义环境变量
  setupFiles: ['<rootDir>/tests/setup.js'],
}
