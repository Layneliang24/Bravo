/**
 * 回归测试配置文件
 * 定义回归测试的各项参数和阈值
 */

module.exports = {
  // 基本配置
  testTimeout: 30000, // 测试超时时间（毫秒）
  retries: 2, // 失败重试次数
  parallel: true, // 是否并行执行
  
  // 环境配置
  environments: {
    local: {
      baseUrl: 'http://localhost:3000',
      apiUrl: 'http://localhost:8000/api',
      dbUrl: 'postgresql://localhost:5432/bravo_test'
    },
    staging: {
      baseUrl: 'https://staging.bravo.com',
      apiUrl: 'https://staging-api.bravo.com/api',
      dbUrl: process.env.STAGING_DB_URL
    },
    production: {
      baseUrl: 'https://bravo.com',
      apiUrl: 'https://api.bravo.com/api',
      dbUrl: process.env.PROD_DB_URL
    }
  },
  
  // API回归测试配置
  api: {
    // 响应时间阈值（毫秒）
    responseTimeThresholds: {
      fast: 200,    // 快速接口（如获取用户信息）
      normal: 500,  // 普通接口（如列表查询）
      slow: 2000    // 慢接口（如复杂计算、文件上传）
    },
    
    // 需要测试的关键API端点
    criticalEndpoints: [
      // 认证相关
      { path: '/auth/login', method: 'POST', category: 'fast' },
      { path: '/auth/logout', method: 'POST', category: 'fast' },
      { path: '/auth/refresh', method: 'POST', category: 'fast' },
      
      // 用户相关
      { path: '/users/profile', method: 'GET', category: 'fast' },
      { path: '/users/list', method: 'GET', category: 'normal' },
      { path: '/users/create', method: 'POST', category: 'normal' },
      
      // 博客相关
      { path: '/blog/posts', method: 'GET', category: 'normal' },
      { path: '/blog/posts/:id', method: 'GET', category: 'fast' },
      { path: '/blog/posts', method: 'POST', category: 'normal' },
      { path: '/blog/posts/:id', method: 'PUT', category: 'normal' },
      { path: '/blog/posts/:id', method: 'DELETE', category: 'fast' },
      
      // 英语学习相关
      { path: '/english/lessons', method: 'GET', category: 'normal' },
      { path: '/english/progress', method: 'GET', category: 'normal' },
      { path: '/english/practice', method: 'POST', category: 'slow' }
    ],
    
    // 响应结构验证
    schemaValidation: {
      enabled: true,
      strictMode: true, // 严格模式：不允许额外字段
      ignoreFields: ['timestamp', 'requestId', 'version'] // 忽略的动态字段
    },
    
    // 数据一致性检查
    dataConsistency: {
      enabled: true,
      checkRelations: true, // 检查关联数据
      checkConstraints: true // 检查数据约束
    }
  },
  
  // UI回归测试配置
  ui: {
    // 浏览器配置
    browsers: [
      { name: 'chromium', viewport: { width: 1280, height: 720 } },
      { name: 'firefox', viewport: { width: 1280, height: 720 } },
      { name: 'webkit', viewport: { width: 1280, height: 720 } }
    ],
    
    // 响应式测试视口
    viewports: [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1280, height: 720 },
      { name: 'large', width: 1920, height: 1080 }
    ],
    
    // 视觉回归配置
    visualRegression: {
      enabled: true,
      threshold: 0.1, // 差异阈值（百分比）
      ignoreAntialiasing: true,
      ignoreColors: false,
      pixelRatio: 1
    },
    
    // 关键页面列表
    criticalPages: [
      { path: '/', name: 'homepage' },
      { path: '/login', name: 'login' },
      { path: '/dashboard', name: 'dashboard' },
      { path: '/blog', name: 'blog-list' },
      { path: '/blog/create', name: 'blog-create' },
      { path: '/profile', name: 'user-profile' },
      { path: '/english', name: 'english-learning' },
      { path: '/english/lessons', name: 'english-lessons' }
    ],
    
    // 关键用户流程
    criticalFlows: [
      {
        name: 'user-registration',
        steps: ['/', '/register', '/verify-email', '/dashboard']
      },
      {
        name: 'blog-creation',
        steps: ['/login', '/dashboard', '/blog/create', '/blog']
      },
      {
        name: 'english-learning',
        steps: ['/login', '/english', '/english/lessons', '/english/practice']
      }
    ]
  },
  
  // 数据回归测试配置
  data: {
    // 数据库快照
    snapshots: {
      enabled: true,
      tables: [
        'users', 'blog_posts', 'english_lessons', 
        'user_progress', 'auth_tokens'
      ],
      excludeFields: ['created_at', 'updated_at', 'last_login'] // 排除时间字段
    },
    
    // 数据一致性检查
    consistency: {
      enabled: true,
      checkForeignKeys: true,
      checkUniqueConstraints: true,
      checkNotNullConstraints: true
    }
  },
  
  // 报告配置
  reporting: {
    formats: ['html', 'json', 'junit'],
    outputDir: './tests/regression/reports',
    includeScreenshots: true,
    includeLogs: true,
    
    // 通知配置
    notifications: {
      enabled: process.env.CI === 'true',
      slack: {
        webhook: process.env.SLACK_WEBHOOK,
        channel: '#testing'
      },
      email: {
        enabled: false,
        recipients: ['team@bravo.com']
      }
    }
  },
  
  // 基线管理
  baseline: {
    autoUpdate: false, // 是否自动更新基线
    updateOnPass: false, // 测试通过时是否更新基线
    storageType: 'filesystem', // 存储类型：filesystem | s3 | git
    
    // Git存储配置（如果使用git存储）
    git: {
      repository: 'git@github.com:company/bravo-baselines.git',
      branch: 'main'
    }
  },
  
  // 性能监控
  performance: {
    enabled: true,
    metrics: [
      'response_time',
      'memory_usage',
      'cpu_usage',
      'database_queries'
    ],
    
    // 性能阈值
    thresholds: {
      response_time: 500, // 毫秒
      memory_usage: 100, // MB
      cpu_usage: 80, // 百分比
      database_queries: 10 // 单个请求的查询数量
    }
  },
  
  // 调试配置
  debug: {
    enabled: process.env.DEBUG === 'true',
    verbose: false,
    saveFailedTests: true,
    keepTestData: false // 测试完成后是否保留测试数据
  }
};