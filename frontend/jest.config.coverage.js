// Jest configuration for coverage thresholds - ANTI-CHEATING
module.exports = {
  // Extend base jest config
  ...require('./jest.config.js'),
  
  // Force coverage collection
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,ts,vue}',
    '!src/**/*.d.ts',
    '!src/main.ts',
    '!src/vite-env.d.ts',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/coverage/**'
  ],
  
  // Coverage output
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'text-summary', 
    'html',
    'lcov',
    'json',
    'json-summary'
  ],
  
  // HARD THRESHOLDS - CI will fail if not met
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    },
    // Per-directory thresholds for critical areas
    './src/components/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    },
    './src/stores/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './src/api/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  
  // Fail fast on threshold violations
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/coverage/',
    '\\.d\\.ts$'
  ],
  
  // Additional reporters for CI
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: './test-results',
        outputName: 'coverage-results.xml',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathForSuiteName: true
      }
    ]
  ],
  
  // Ensure tests run in CI mode
  ci: true,
  watchAll: false,
  
  // Verbose output for debugging
  verbose: true,
  
  // Custom threshold checking script
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup.ts',
    '<rootDir>/tests/coverage-setup.js'
  ]
};