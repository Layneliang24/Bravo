#!/usr/bin/env node

/**
 * 回归测试运行器
 * 统一入口，支持不同类型的回归测试
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync, spawn } = require('child_process');
const config = require('./config/regression.config');

class RegressionTestRunner {
  constructor() {
    this.config = config;
    this.results = {
      api: [],
      ui: [],
      db: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        errors: 0,
        baselines: 0
      }
    };
  }
  
  /**
   * 运行所有回归测试
   * @param {Object} options - 运行选项
   */
  async runAll(options = {}) {
    console.log('🚀 Starting regression test suite...');
    console.log('=' .repeat(50));
    
    const startTime = Date.now();
    
    try {
      // 检查环境
      await this.checkEnvironment();
      
      // 运行测试
      if (options.api !== false) {
        await this.runApiTests(options);
      }
      
      if (options.ui !== false) {
        await this.runUiTests(options);
      }
      
      if (options.db !== false) {
        await this.runDbTests(options);
      }
      
      // 生成报告
      const report = await this.generateReport();
      
      // 保存报告
      await this.saveReport(report);
      
      const duration = Date.now() - startTime;
      console.log('\n' + '=' .repeat(50));
      console.log(`✅ Regression tests completed in ${duration}ms`);
      console.log(`📊 Results: ${this.results.summary.passed} passed, ${this.results.summary.failed} failed, ${this.results.summary.errors} errors`);
      
      if (this.results.summary.failed > 0 || this.results.summary.errors > 0) {
        console.log('❌ Some tests failed. Check the detailed report.');
        process.exit(1);
      } else {
        console.log('🎉 All regression tests passed!');
      }
      
    } catch (error) {
      console.error('💥 Regression test suite failed:', error.message);
      process.exit(1);
    }
  }
  
  /**
   * 检查测试环境
   */
  async checkEnvironment() {
    console.log('🔍 Checking test environment...');
    
    // 检查必要的目录
    const requiredDirs = [
      './tests/regression/data/snapshots',
      './tests/regression/config/baselines',
      './tests/regression/reports'
    ];
    
    for (const dir of requiredDirs) {
      try {
        await fs.access(dir);
      } catch {
        await fs.mkdir(dir, { recursive: true });
        console.log(`📁 Created directory: ${dir}`);
      }
    }
    
    // 检查配置文件
    try {
      await fs.access('./tests/regression/config/regression.config.js');
    } catch {
      throw new Error('Configuration file not found: ./tests/regression/config/regression.config.js');
    }
    
    // 检查依赖
    const dependencies = ['jest', 'playwright', 'axios'];
    for (const dep of dependencies) {
      try {
        require.resolve(dep);
      } catch {
        console.warn(`⚠️  Dependency ${dep} not found. Some tests may fail.`);
      }
    }
    
    console.log('✅ Environment check completed');
  }
  
  /**
   * 运行API回归测试
   * @param {Object} options - 选项
   */
  async runApiTests(options = {}) {
    if (!this.config.api.enabled) {
      console.log('⏭️  API tests disabled, skipping...');
      return;
    }
    
    console.log('\n🌐 Running API regression tests...');
    
    try {
      const testCommand = this.buildJestCommand('api', options);
      const result = await this.executeCommand(testCommand);
      
      this.results.api = this.parseJestResults(result);
      this.updateSummary(this.results.api);
      
      console.log(`✅ API tests completed: ${this.results.api.length} tests`);
      
    } catch (error) {
      console.error('❌ API tests failed:', error.message);
      this.results.summary.errors++;
    }
  }
  
  /**
   * 运行UI回归测试
   * @param {Object} options - 选项
   */
  async runUiTests(options = {}) {
    if (!this.config.ui.enabled) {
      console.log('⏭️  UI tests disabled, skipping...');
      return;
    }
    
    console.log('\n🎨 Running UI regression tests...');
    
    try {
      const testCommand = this.buildPlaywrightCommand(options);
      const result = await this.executeCommand(testCommand);
      
      this.results.ui = this.parsePlaywrightResults(result);
      this.updateSummary(this.results.ui);
      
      console.log(`✅ UI tests completed: ${this.results.ui.length} tests`);
      
    } catch (error) {
      console.error('❌ UI tests failed:', error.message);
      this.results.summary.errors++;
    }
  }
  
  /**
   * 运行数据库回归测试
   * @param {Object} options - 选项
   */
  async runDbTests(options = {}) {
    if (!this.config.database.enabled) {
      console.log('⏭️  Database tests disabled, skipping...');
      return;
    }
    
    console.log('\n🗄️  Running database regression tests...');
    
    try {
      const testCommand = this.buildJestCommand('data', options);
      const result = await this.executeCommand(testCommand);
      
      this.results.db = this.parseJestResults(result);
      this.updateSummary(this.results.db);
      
      console.log(`✅ Database tests completed: ${this.results.db.length} tests`);
      
    } catch (error) {
      console.error('❌ Database tests failed:', error.message);
      this.results.summary.errors++;
    }
  }
  
  /**
   * 构建Jest命令
   * @param {string} testType - 测试类型
   * @param {Object} options - 选项
   */
  buildJestCommand(testType, options = {}) {
    const baseCommand = 'npx jest';
    const testPattern = `./tests/regression/${testType}/**/*.test.js`;
    
    let command = `${baseCommand} ${testPattern}`;
    
    // 添加选项
    if (options.verbose) {
      command += ' --verbose';
    }
    
    if (options.updateSnapshots) {
      command += ' --updateSnapshot';
    }
    
    if (options.maxWorkers) {
      command += ` --maxWorkers=${options.maxWorkers}`;
    }
    
    // 添加JSON输出用于解析结果
    command += ' --json --outputFile=./tests/regression/reports/jest-results.json';
    
    return command;
  }
  
  /**
   * 构建Playwright命令
   * @param {Object} options - 选项
   */
  buildPlaywrightCommand(options = {}) {
    const baseCommand = 'npx playwright test';
    const testPattern = './tests/regression/ui/**/*.test.js';
    
    let command = `${baseCommand} ${testPattern}`;
    
    // 添加选项
    if (options.headed) {
      command += ' --headed';
    }
    
    if (options.browser) {
      command += ` --project=${options.browser}`;
    }
    
    if (options.updateSnapshots) {
      command += ' --update-snapshots';
    }
    
    // 添加报告输出
    command += ' --reporter=json --output-dir=./tests/regression/reports';
    
    return command;
  }
  
  /**
   * 执行命令
   * @param {string} command - 命令
   */
  async executeCommand(command) {
    return new Promise((resolve, reject) => {
      console.log(`🔧 Executing: ${command}`);
      
      const child = spawn(command, {
        shell: true,
        stdio: ['inherit', 'pipe', 'pipe']
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
        if (!process.env.SILENT) {
          process.stdout.write(data);
        }
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
        if (!process.env.SILENT) {
          process.stderr.write(data);
        }
      });
      
      child.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });
      
      child.on('error', (error) => {
        reject(error);
      });
    });
  }
  
  /**
   * 解析Jest结果
   * @param {Object} result - 命令执行结果
   */
  parseJestResults(result) {
    try {
      const reportPath = './tests/regression/reports/jest-results.json';
      const reportContent = require(path.resolve(reportPath));
      
      return reportContent.testResults.map(testFile => ({
        file: testFile.name,
        tests: testFile.assertionResults.map(test => ({
          name: test.title,
          status: test.status,
          duration: test.duration,
          error: test.failureMessages.join('\n')
        }))
      }));
    } catch (error) {
      console.warn('Failed to parse Jest results:', error.message);
      return [];
    }
  }
  
  /**
   * 解析Playwright结果
   * @param {Object} result - 命令执行结果
   */
  parsePlaywrightResults(result) {
    try {
      const reportPath = './tests/regression/reports/results.json';
      const reportContent = require(path.resolve(reportPath));
      
      return reportContent.suites.flatMap(suite => 
        suite.specs.map(spec => ({
          name: spec.title,
          status: spec.tests[0]?.results[0]?.status || 'unknown',
          duration: spec.tests[0]?.results[0]?.duration || 0,
          error: spec.tests[0]?.results[0]?.error?.message || ''
        }))
      );
    } catch (error) {
      console.warn('Failed to parse Playwright results:', error.message);
      return [];
    }
  }
  
  /**
   * 更新汇总统计
   * @param {Array} testResults - 测试结果
   */
  updateSummary(testResults) {
    testResults.forEach(testFile => {
      if (testFile.tests) {
        testFile.tests.forEach(test => {
          this.results.summary.total++;
          
          switch (test.status) {
            case 'passed':
              this.results.summary.passed++;
              break;
            case 'failed':
              this.results.summary.failed++;
              break;
            case 'baseline_created':
              this.results.summary.baselines++;
              break;
            default:
              this.results.summary.errors++;
          }
        });
      }
    });
  }
  
  /**
   * 生成测试报告
   */
  async generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      config: this.config,
      summary: this.results.summary,
      results: {
        api: this.results.api,
        ui: this.results.ui,
        db: this.results.db
      },
      environment: {
        node: process.version,
        platform: process.platform,
        arch: process.arch,
        cwd: process.cwd()
      }
    };
    
    return report;
  }
  
  /**
   * 保存测试报告
   * @param {Object} report - 报告数据
   */
  async saveReport(report) {
    const reportPath = './tests/regression/reports/regression-report.json';
    const htmlReportPath = './tests/regression/reports/regression-report.html';
    
    // 保存JSON报告
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 Report saved: ${reportPath}`);
    
    // 生成HTML报告
    const htmlReport = this.generateHtmlReport(report);
    await fs.writeFile(htmlReportPath, htmlReport);
    console.log(`🌐 HTML report saved: ${htmlReportPath}`);
  }
  
  /**
   * 生成HTML报告
   * @param {Object} report - 报告数据
   */
  generateHtmlReport(report) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regression Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .passed { background: #d4edda; }
        .failed { background: #f8d7da; }
        .error { background: #fff3cd; }
        .section { margin: 20px 0; }
        .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .test-passed { border-color: #28a745; }
        .test-failed { border-color: #dc3545; }
        .test-error { border-color: #ffc107; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Regression Test Report</h1>
        <p><strong>Generated:</strong> ${report.timestamp}</p>
        <p><strong>Environment:</strong> Node ${report.environment.node} on ${report.environment.platform}</p>
    </div>
    
    <div class="summary">
        <div class="stat passed">
            <h3>${report.summary.passed}</h3>
            <p>Passed</p>
        </div>
        <div class="stat failed">
            <h3>${report.summary.failed}</h3>
            <p>Failed</p>
        </div>
        <div class="stat error">
            <h3>${report.summary.errors}</h3>
            <p>Errors</p>
        </div>
        <div class="stat">
            <h3>${report.summary.baselines}</h3>
            <p>Baselines Created</p>
        </div>
    </div>
    
    ${this.generateTestSectionHtml('API Tests', report.results.api)}
    ${this.generateTestSectionHtml('UI Tests', report.results.ui)}
    ${this.generateTestSectionHtml('Database Tests', report.results.db)}
    
    <div class="section">
        <h2>📋 Configuration</h2>
        <pre>${JSON.stringify(report.config, null, 2)}</pre>
    </div>
</body>
</html>
    `;
  }
  
  /**
   * 生成测试部分HTML
   * @param {string} title - 标题
   * @param {Array} results - 结果
   */
  generateTestSectionHtml(title, results) {
    if (!results || results.length === 0) {
      return `<div class="section"><h2>${title}</h2><p>No tests run</p></div>`;
    }
    
    const testsHtml = results.flatMap(testFile => 
      testFile.tests.map(test => `
        <div class="test-result test-${test.status}">
            <strong>${test.name}</strong>
            <span style="float: right;">${test.status} (${test.duration}ms)</span>
            ${test.error ? `<pre>${test.error}</pre>` : ''}
        </div>
      `)
    ).join('');
    
    return `
      <div class="section">
          <h2>${title}</h2>
          ${testsHtml}
      </div>
    `;
  }
}

// CLI接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};
  
  // 解析命令行参数
  args.forEach(arg => {
    if (arg === '--verbose') options.verbose = true;
    if (arg === '--update-snapshots') options.updateSnapshots = true;
    if (arg === '--headed') options.headed = true;
    if (arg === '--api-only') { options.ui = false; options.db = false; }
    if (arg === '--ui-only') { options.api = false; options.db = false; }
    if (arg === '--db-only') { options.api = false; options.ui = false; }
    if (arg.startsWith('--browser=')) options.browser = arg.split('=')[1];
    if (arg.startsWith('--max-workers=')) options.maxWorkers = arg.split('=')[1];
  });
  
  const runner = new RegressionTestRunner();
  runner.runAll(options).catch(error => {
    console.error('Failed to run regression tests:', error);
    process.exit(1);
  });
}

module.exports = RegressionTestRunner;