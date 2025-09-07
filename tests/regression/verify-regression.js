#!/usr/bin/env node

/**
 * 回归测试验证脚本
 * 快速验证回归测试框架是否正常工作
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

class RegressionVerifier {
  constructor() {
    // 从 tests/regression 目录向上两级到达项目根目录
    this.projectRoot = path.resolve(__dirname, '../..');
    this.regressionDir = path.resolve(__dirname);
    this.checks = [
      { name: '配置文件检查', method: 'checkConfig' },
      { name: '依赖检查', method: 'checkDependencies' },
      { name: '测试文件检查', method: 'checkTestFiles' },
      { name: '快照目录检查', method: 'checkSnapshotDirs' },
      { name: '基本功能测试', method: 'runBasicTests' }
    ];
  }

  /**
   * 运行所有验证检查
   */
  async verify() {
    console.log('🔍 验证回归测试框架...');
    console.log('=' .repeat(50));
    
    const results = [];
    
    for (const check of this.checks) {
      try {
        console.log(`\n📋 ${check.name}...`);
        const result = await this[check.method]();
        results.push({ ...check, success: true, result });
        console.log('✅ 通过');
      } catch (error) {
        results.push({ ...check, success: false, error: error.message });
        console.log(`❌ 失败: ${error.message}`);
      }
    }
    
    // 生成验证报告
    await this.generateVerificationReport(results);
    
    const passed = results.filter(r => r.success).length;
    const total = results.length;
    
    console.log('\n' + '=' .repeat(50));
    console.log(`📊 验证结果: ${passed}/${total} 项检查通过`);
    
    if (passed === total) {
      console.log('🎉 回归测试框架验证成功！');
      console.log('\n💡 使用方法:');
      console.log('   make test-regression          # 运行所有回归测试');
      console.log('   make test-regression-api      # 运行API回归测试');
      console.log('   make test-regression-ui       # 运行UI回归测试');
      console.log('   make test-regression-db       # 运行数据库回归测试');
      console.log('   make test-regression-update   # 更新回归测试基线');
    } else {
      console.log('⚠️  部分检查未通过，请查看详细报告');
      process.exit(1);
    }
  }

  /**
   * 检查配置文件
   */
  async checkConfig() {
    const configPath = path.join(this.regressionDir, 'config/regression.config.js');
    
    // 检查配置文件是否存在
    await fs.access(configPath);
    
    // 尝试加载配置
    const config = require(configPath);
    
    // 验证关键配置项
    const requiredKeys = ['api', 'ui', 'data', 'reporting'];
    for (const key of requiredKeys) {
      if (!config[key]) {
        throw new Error(`缺少配置项: ${key}`);
      }
    }
    
    return {
      configFile: '存在',
      apiEndpoints: config.api.criticalEndpoints?.length || 0,
      uiPages: config.ui.criticalPages?.length || 0,
      dbTables: config.data.snapshots?.tables?.length || 0
    };
  }

  /**
   * 检查依赖
   */
  async checkDependencies() {
    // 尝试多个可能的package.json位置
    const possiblePaths = [
      path.join(this.projectRoot, 'package.json'),
      path.join(this.projectRoot, 'frontend/package.json'),
      path.join(this.projectRoot, 'e2e/package.json')
    ];
    
    let packageJson = null;
    let packageJsonPath = null;
    
    for (const testPath of possiblePaths) {
      try {
        await fs.access(testPath);
        packageJson = JSON.parse(await fs.readFile(testPath, 'utf8'));
        packageJsonPath = testPath;
        break;
      } catch (error) {
        // 继续尝试下一个路径
      }
    }
    
    if (!packageJson) {
      throw new Error(`未找到package.json文件，尝试的路径: ${possiblePaths.join(', ')}`);
    }
    
    // 检查各个子项目的关键依赖
    const dependencyChecks = {
      'axios': { found: false, location: '', version: '', description: 'HTTP请求库' },
      'playwright': { found: false, location: '', version: '', description: 'UI测试框架' },
      'vitest': { found: false, location: '', version: '', description: '测试框架' },
      'jest': { found: false, location: '', version: '', description: '测试框架(备选)' }
    };
    
    // 检查所有package.json文件
    const allPackageJsons = [
      { path: packageJsonPath, data: packageJson, name: '根目录' },
    ];
    
    // 尝试加载其他package.json
    const otherPaths = [
      { path: path.join(this.projectRoot, 'frontend/package.json'), name: '前端' },
      { path: path.join(this.projectRoot, 'e2e/package.json'), name: 'E2E测试' }
    ];
    
    for (const { path: pkgPath, name } of otherPaths) {
      try {
        const data = JSON.parse(await fs.readFile(pkgPath, 'utf8'));
        allPackageJsons.push({ path: pkgPath, data, name });
      } catch (error) {
        // 忽略不存在的package.json
      }
    }
    
    // 检查依赖
    for (const { data, name } of allPackageJsons) {
      for (const [dep, info] of Object.entries(dependencyChecks)) {
        if (!info.found) {
          const version = data.dependencies?.[dep] || data.devDependencies?.[dep];
          if (version) {
            info.found = true;
            info.location = name;
            info.version = version;
          }
        }
      }
    }
    
    // 检查关键依赖是否存在
    const criticalDeps = ['axios', 'playwright'];
    const missing = criticalDeps.filter(dep => !dependencyChecks[dep].found);
    
    if (missing.length > 0) {
      throw new Error(`缺少关键依赖: ${missing.join(', ')}`);
    }
    
    const installed = Object.entries(dependencyChecks)
      .filter(([_, info]) => info.found)
      .map(([dep, info]) => ({ dep, ...info }));
    
    return { installed, missing: [], packageJsons: allPackageJsons.length };
  }

  /**
   * 检查测试文件
   */
  async checkTestFiles() {
    const testFiles = [
      'api/api-regression.test.js',
      'ui/ui-regression.test.js',
      'data/db-regression.test.js',
      'utils/snapshot.js',
      'run-regression.js'
    ];
    
    const results = [];
    
    for (const file of testFiles) {
      const filePath = path.join(this.regressionDir, file);
      try {
        const stats = await fs.stat(filePath);
        results.push({ file, exists: true, size: stats.size });
      } catch (error) {
        results.push({ file, exists: false, error: error.message });
      }
    }
    
    const missing = results.filter(r => !r.exists);
    if (missing.length > 0) {
      throw new Error(`缺少测试文件: ${missing.map(m => m.file).join(', ')}`);
    }
    
    return results;
  }

  /**
   * 检查快照目录
   */
  async checkSnapshotDirs() {
    const snapshotDirs = [
      'snapshots/api',
      'snapshots/ui',
      'snapshots/db',
      'reports'
    ];
    
    const results = [];
    
    for (const dir of snapshotDirs) {
      const dirPath = path.join(this.regressionDir, dir);
      try {
        await fs.mkdir(dirPath, { recursive: true });
        results.push({ dir, exists: true });
      } catch (error) {
        results.push({ dir, exists: false, error: error.message });
      }
    }
    
    return results;
  }

  /**
   * 运行基本功能测试
   */
  async runBasicTests() {
    const tests = [
      {
        name: '配置加载测试',
        test: () => {
          const config = require('./config/regression.config.js');
          return config.api && config.ui && config.data;
        }
      },
      {
        name: '快照管理器测试',
        test: () => {
          const SnapshotManager = require('./utils/snapshot.js');
          const manager = new SnapshotManager();
          return typeof manager.createApiSnapshot === 'function';
        }
      },
      {
        name: '测试运行器测试',
        test: () => {
          const RegressionTestRunner = require('./run-regression.js');
          const runner = new RegressionTestRunner();
          return typeof runner.runAll === 'function';
        }
      }
    ];
    
    const results = [];
    
    for (const test of tests) {
      try {
        const result = test.test();
        results.push({ name: test.name, success: true, result });
      } catch (error) {
        results.push({ name: test.name, success: false, error: error.message });
      }
    }
    
    const failed = results.filter(r => !r.success);
    if (failed.length > 0) {
      throw new Error(`功能测试失败: ${failed.map(f => f.name).join(', ')}`);
    }
    
    return results;
  }

  /**
   * 生成验证报告
   */
  async generateVerificationReport(results) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: results.length,
        passed: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length
      },
      checks: results,
      recommendations: this.generateRecommendations(results)
    };
    
    const reportPath = path.join(this.regressionDir, 'verification-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    // 生成HTML报告
    const htmlReport = this.generateHtmlReport(report);
    const htmlPath = path.join(this.regressionDir, 'verification-report.html');
    await fs.writeFile(htmlPath, htmlReport);
  }

  /**
   * 生成建议
   */
  generateRecommendations(results) {
    const recommendations = [];
    
    const failed = results.filter(r => !r.success);
    
    if (failed.length === 0) {
      recommendations.push('✅ 回归测试框架已就绪，可以开始使用');
      recommendations.push('📝 建议先运行一次完整的回归测试建立基线');
      recommendations.push('🔄 定期更新回归测试用例以覆盖新功能');
    } else {
      recommendations.push('⚠️ 请先解决验证失败的问题');
      
      failed.forEach(f => {
        switch (f.name) {
          case '依赖检查':
            recommendations.push('📦 运行 npm install 安装缺少的依赖');
            break;
          case '测试文件检查':
            recommendations.push('📁 检查测试文件是否正确创建');
            break;
          case '基本功能测试':
            recommendations.push('🔧 检查代码语法和模块导入');
            break;
        }
      });
    }
    
    return recommendations;
  }

  /**
   * 生成HTML报告
   */
  generateHtmlReport(report) {
    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>回归测试验证报告</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .content { padding: 30px; }
        .summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .summary-item { text-align: center; padding: 20px; border-radius: 6px; }
        .summary-total { background: #e3f2fd; }
        .summary-passed { background: #e8f5e8; }
        .summary-failed { background: #ffebee; }
        .check-item { margin-bottom: 20px; padding: 15px; border-radius: 6px; border-left: 4px solid #ddd; }
        .check-success { border-left-color: #28a745; background: #f8fff8; }
        .check-failed { border-left-color: #dc3545; background: #fff8f8; }
        .recommendations { background: #fff3cd; padding: 20px; border-radius: 6px; }
        .timestamp { color: #666; font-size: 0.9em; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 回归测试验证报告</h1>
            <p>验证回归测试框架的完整性和可用性</p>
            <p class="timestamp">生成时间: ${new Date(report.timestamp).toLocaleString('zh-CN')}</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <div class="summary-item summary-total">
                    <h3>${report.summary.total}</h3>
                    <p>总检查项</p>
                </div>
                <div class="summary-item summary-passed">
                    <h3>${report.summary.passed}</h3>
                    <p>通过</p>
                </div>
                <div class="summary-item summary-failed">
                    <h3>${report.summary.failed}</h3>
                    <p>失败</p>
                </div>
            </div>
            
            <h2>📋 检查详情</h2>
            ${report.checks.map(check => `
                <div class="check-item ${check.success ? 'check-success' : 'check-failed'}">
                    <h3>${check.success ? '✅' : '❌'} ${check.name}</h3>
                    ${check.success ? 
                        (check.result ? `<pre>${JSON.stringify(check.result, null, 2)}</pre>` : '<p>检查通过</p>') :
                        `<p><strong>错误:</strong> ${check.error}</p>`
                    }
                </div>
            `).join('')}
            
            <h2>💡 建议</h2>
            <div class="recommendations">
                <ul>
                    ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            <h2>🚀 快速开始</h2>
            <p>如果所有检查都通过，你可以开始使用回归测试:</p>
            <pre><code># 验证回归测试框架
node tests/regression/verify-regression.js

# 运行回归测试演示
node tests/regression/demo/regression-demo.js

# 运行实际的回归测试
make test-regression</code></pre>
        </div>
    </div>
</body>
</html>
    `;
  }
}

// CLI入口
if (require.main === module) {
  const verifier = new RegressionVerifier();
  verifier.verify().catch(error => {
    console.error('验证失败:', error);
    process.exit(1);
  });
}

module.exports = RegressionVerifier;