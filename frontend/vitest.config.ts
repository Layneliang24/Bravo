import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: [
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache',
      'tests/e2e/**'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/*.setup.{js,ts}',
        'src/main.ts',
        'src/App.vue',
        'src/assets/**',
        'src/styles/**',
        'src/types/**',
        '**/*.stories.{js,ts}',
        '**/*.story.{js,ts}'
      ],
      include: [
        'src/**/*.{js,ts,vue}'
      ],
      all: true,
      lines: 75,
      functions: 75,
      branches: 70,
      statements: 75,
      // 阈值配置移到coverage外部
      watermarks: {
        lines: [70, 75],
        functions: [70, 75],
        branches: [65, 70],
        statements: [70, 75]
      }
    },
    reporters: ['verbose', 'junit'],
    outputFile: {
      junit: './tests/reports/junit.xml'
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 5000,
    isolate: true,
    watch: false,
    ui: false,
    open: false,
    api: {
      port: 51204
    }
  }
})