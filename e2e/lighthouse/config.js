// Lighthouse 配置文件
// 用于自定义性能审计的配置选项

module.exports = {
  // 扩展默认配置
  extends: 'lighthouse:default',
  
  // 自定义设置
  settings: {
    // 仅在桌面模式下运行
    formFactor: 'desktop',
    
    // 网络和CPU节流设置
    throttling: {
      rttMs: 40,
      throughputKbps: 10240,
      cpuSlowdownMultiplier: 1,
      requestLatencyMs: 0,
      downloadThroughputKbps: 0,
      uploadThroughputKbps: 0
    },
    
    // 屏幕模拟设置
    screenEmulation: {
      mobile: false,
      width: 1350,
      height: 940,
      deviceScaleFactor: 1,
      disabled: false
    },
    
    // 用户代理
    emulatedUserAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36 lighthouse',
    
    // 审计配置
    onlyAudits: [
      // 性能指标
      'first-contentful-paint',
      'largest-contentful-paint',
      'first-meaningful-paint',
      'speed-index',
      'total-blocking-time',
      'cumulative-layout-shift',
      'interactive',
      
      // 资源优化
      'unused-css-rules',
      'unused-javascript',
      'modern-image-formats',
      'uses-optimized-images',
      'uses-webp-images',
      'uses-responsive-images',
      
      // 网络优化
      'uses-http2',
      'uses-long-cache-ttl',
      'efficient-animated-content',
      
      // 可访问性
      'color-contrast',
      'image-alt',
      'label',
      'link-name',
      
      // SEO
      'document-title',
      'meta-description',
      'http-status-code',
      'link-text',
      'is-crawlable',
      
      // 最佳实践
      'is-on-https',
      'uses-passive-event-listeners',
      'no-document-write',
      'external-anchors-use-rel-noopener',
      'geolocation-on-start',
      'notification-on-start'
    ]
  },
  
  // 自定义审计类别权重
  categories: {
    performance: {
      title: '性能',
      description: '这些检查确保您的页面针对速度进行了优化。',
      auditRefs: [
        {id: 'first-contentful-paint', weight: 10, group: 'metrics'},
        {id: 'largest-contentful-paint', weight: 25, group: 'metrics'},
        {id: 'first-meaningful-paint', weight: 10, group: 'metrics'},
        {id: 'speed-index', weight: 10, group: 'metrics'},
        {id: 'total-blocking-time', weight: 30, group: 'metrics'},
        {id: 'cumulative-layout-shift', weight: 15, group: 'metrics'},
        {id: 'interactive', weight: 10, group: 'metrics'}
      ]
    }
  },
  
  // 审计组
  groups: {
    metrics: {
      title: '指标'
    },
    'load-opportunities': {
      title: '优化建议',
      description: '这些建议可以让您的页面加载更快。它们不会直接影响性能评分。'
    },
    diagnostics: {
      title: '诊断',
      description: '有关应用程序性能的更多信息。'
    }
  }
};