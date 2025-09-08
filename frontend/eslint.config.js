// ESLint v9 配置文件 - 适用于Vue 3 + TypeScript项目
import js from '@eslint/js';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import vue from 'eslint-plugin-vue';
import vueParser from 'vue-eslint-parser';
import prettier from 'eslint-config-prettier';

export default [
  // 基础JavaScript推荐配置
  js.configs.recommended,
  // Vue 3推荐配置（扁平化配置格式）
  ...vue.configs['flat/recommended'],
  // Prettier配置，禁用与Prettier冲突的ESLint规则
  prettier,
  // 主要配置块：适用于所有JS/TS/Vue文件
  {
    files: ['**/*.{js,ts,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        parser: typescriptParser,
        sourceType: 'module',
      },
      // 全局变量定义，避免no-undef错误
      globals: {
        console: 'readonly',      // 浏览器和Node.js控制台
        process: 'readonly',      // Node.js进程对象
        __dirname: 'readonly',    // Node.js当前目录路径
        __filename: 'readonly',   // Node.js当前文件路径
        module: 'readonly',       // Node.js模块对象
        require: 'readonly',      // Node.js require函数
        global: 'readonly',       // Node.js全局对象
        Buffer: 'readonly',       // Node.js Buffer类
        setTimeout: 'readonly',   // 定时器函数
        clearTimeout: 'readonly', // 清除定时器函数
        setInterval: 'readonly',  // 间隔定时器函数
        clearInterval: 'readonly',// 清除间隔定时器函数
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
      vue,
    },
    rules: {
      // 命名规则检查
      'camelcase': ['error', { properties: 'always' }], // 强制使用驼峰命名
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'default',           // 默认规则：所有标识符使用camelCase
          format: ['camelCase'],
          leadingUnderscore: 'allow',    // 允许前导下划线（私有成员约定）
          trailingUnderscore: 'allow',   // 允许尾随下划线
        },
        {
          selector: 'variable',          // 变量：允许camelCase和UPPER_CASE（常量）
          format: ['camelCase', 'UPPER_CASE'],
        },
        {
          selector: 'typeLike',          // 类型相关：使用PascalCase（类、接口、枚举等）
          format: ['PascalCase'],
        },
        {
          selector: 'property',
          format: ['camelCase', 'PascalCase', 'UPPER_CASE'],
          filter: {
            // 排除以下特殊属性名的命名规范检查：
            // - @开头：Vue组件属性绑定语法（如@click）
            // - COVERAGE_THRESHOLDS：测试覆盖率配置常量
            // - router-link/router-view：Vue Router组件名
            // - ./开头：文件路径配置（如Jest配置中的路径映射）
            regex: '^(@|COVERAGE_THRESHOLDS|router-link|router-view|\\./)',
            match: false,
          },
        },
        {
          selector: 'import',            // 导入名称：允许camelCase和PascalCase
          format: ['camelCase', 'PascalCase'],
        },
      ],
      
      // Vue 特定规则
      'vue/component-name-in-template-casing': ['error', 'PascalCase'], // 模板中组件名使用PascalCase
      'vue/prop-name-casing': ['error', 'camelCase'],                   // Props使用camelCase命名
      'vue/attribute-hyphenation': ['error', 'always'],                 // 属性名使用kebab-case
      'vue/v-on-event-hyphenation': ['error', 'always'],               // 事件名使用kebab-case
      'vue/multi-word-component-names': 'off',                         // 允许单词组件名（如App.vue）
      
      // TypeScript 规则
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }], // 未使用变量检查，忽略_开头的参数
      '@typescript-eslint/explicit-function-return-type': 'off',       // 不强制函数返回类型声明
      '@typescript-eslint/explicit-module-boundary-types': 'off',      // 不强制模块边界类型声明
      '@typescript-eslint/no-explicit-any': 'warn',                    // any类型使用警告
      
      // 通用规则
      'no-console': 'warn',      // console使用警告
      'no-debugger': 'error',    // 禁止debugger语句
      'prefer-const': 'error',   // 优先使用const
      'no-var': 'error',         // 禁止使用var
    },
  },
  // TypeScript文件特定配置
  {
    files: ['**/*.ts', '**/*.tsx'],
    rules: {
      '@typescript-eslint/explicit-function-return-type': 'warn', // TS文件中函数返回类型警告
    },
  },
  // 测试文件特定规则
  {
    files: ['tests/**/*', '**/*.test.{js,ts}', '**/*.spec.{js,ts}'],
    rules: {
      'no-console': 'off',                        // 测试文件中允许console
      '@typescript-eslint/no-explicit-any': 'off', // 测试文件中允许any类型
    },
  },
  // 配置文件特定规则
  {
    files: ['*.config.{js,ts}', 'vite.config.ts', 'vitest.config.ts', 'jest.config.js', 'jest.config.*.js', 'tests/**/*'],
    rules: {
      '@typescript-eslint/naming-convention': 'off', // 配置文件中关闭命名规范检查
      'no-undef': 'off',                            // 配置文件中关闭未定义变量检查
    },
  },
];