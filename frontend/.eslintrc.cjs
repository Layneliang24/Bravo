module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // 基本规则
    'no-console': 'warn',
    'no-debugger': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    'no-unused-vars': 'off', // 暂时禁用，因为可能与TypeScript冲突
  },
  globals: {
    console: 'readonly',
    process: 'readonly',
    __dirname: 'readonly',
    __filename: 'readonly',
    module: 'readonly',
    require: 'readonly',
    global: 'readonly',
    Buffer: 'readonly',
  },
  overrides: [
    {
      // 测试文件配置
      files: ['tests/**/*.js', '**/*.test.js', '**/*.spec.js'],
      env: {
        jest: true,
        node: true,
      },
      rules: {
        'no-console': 'off', // 测试文件允许 console
      },
    },
  ],
};
