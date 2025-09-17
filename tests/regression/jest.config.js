/**
 * Jest配置文件 - 回归测试
 */

module.exports = {
  // 测试环境
  testEnvironment: "node",

  // 测试文件匹配模式
  testMatch: ["**/*.test.js", "**/*.spec.js"],

  // 测试超时时间
  testTimeout: 30000,

  // 覆盖率配置
  collectCoverage: false,
  collectCoverageFrom: [
    "**/*.js",
    "!**/node_modules/**",
    "!**/coverage/**",
    "!jest.config.js",
  ],

  // 设置文件
  setupFilesAfterEnv: [],

  // 模块路径映射
  moduleNameMapper: {},

  // 转换配置
  transform: {
    "^.+\\.js$": "babel-jest",
  },

  // 转换忽略模式
  transformIgnorePatterns: ["node_modules/(?!(pixelmatch)/)"],

  // 忽略的文件
  testPathIgnorePatterns: [
    "/node_modules/",
    "/coverage/",
    "/reports/",
    "/ui/", // 排除UI测试，使用Playwright单独运行
  ],

  // 报告器
  reporters: [
    "default",
    [
      "jest-junit",
      {
        outputDirectory: "./reports",
        outputName: "regression-test-results.xml",
      },
    ],
  ],

  // 全局变量
  globals: {
    "process.env.NODE_ENV": "test",
  },

  // 详细输出
  verbose: true,

  // 失败时停止
  bail: false,

  // 最大并发数
  maxConcurrency: 5,
};
