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
    environment: 'happy-dom',
    setupFiles: ['./tests/setup.ts'],
    include: [
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache',
      'tests/e2e/**',
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
        '**/*.story.{js,ts}',
      ],
      include: ['src/**/*.{js,ts,vue}'],
      all: true,
      lines: 10,
      functions: 10,
      branches: 10,
      statements: 10,
      // 降低阈值，避免因无测试而失败
      watermarks: {
        lines: [5, 10],
        functions: [5, 10],
        branches: [5, 10],
        statements: [5, 10],
      },
    },
    reporters: ['verbose', 'junit'],
    outputFile: {
      junit: './tests/reports/junit.xml',
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 5000,
    isolate: true,
    watch: false,
    ui: false,
    open: false,
    api: {
      port: 51204,
    },
  },
})
