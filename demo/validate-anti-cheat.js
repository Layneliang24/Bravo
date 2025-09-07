#!/usr/bin/env node
/**
 * 防作弊系统自动化验证脚本
 * 模拟各种作弊场景并验证系统检测能力
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');

class AntiCheatValidator {
  constructor() {
    this.results = [];
    this.backupFiles = new Map();
    this.tempFiles = [];
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const colors = {
      info: chalk.blue,
      success: chalk.green,
      error: chalk.red,
      warning: chalk.yellow
    };
    
    console.log(`[${timestamp}] ${colors[type](message)}`);
  }

  async runCommand(command, expectFailure = false) {
    try {
      const output = execSync(command, { 
        encoding: 'utf8', 
        cwd: process.cwd(),
        stdio: 'pipe'
      });
      
      if (expectFailure) {
        this.log(`❌ 预期失败但成功了: ${command}`, 'error');
        return { success: false, output, expected: false };
      }
      
      this.log(`✅ 命令成功: ${command}`, 'success');
      return { success: true, output, expected: true };
    } catch (error) {
      if (expectFailure) {
        this.log(`✅ 预期失败且确实失败: ${command}`, 'success');
        return { success: false, output: error.message, expected: true };
      }
      
      this.log(`❌ 命令失败: ${command} - ${error.message}`, 'error');
      return { success: false, output: error.message, expected: false };
    }
  }

  backupFile(filePath) {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      this.backupFiles.set(filePath, content);
      this.log(`📁 备份文件: ${filePath}`, 'info');
    }
  }

  restoreFile(filePath) {
    if (this.backupFiles.has(filePath)) {
      fs.writeFileSync(filePath, this.backupFiles.get(filePath));
      this.log(`🔄 恢复文件: ${filePath}`, 'info');
    }
  }

  createTempFile(filePath, content) {
    fs.writeFileSync(filePath, content);
    this.tempFiles.push(filePath);
    this.log(`📝 创建临时文件: ${filePath}`, 'info');
  }

  cleanup() {
    // 恢复备份文件
    for (const [filePath] of this.backupFiles) {
      this.restoreFile(filePath);
    }
    
    // 删除临时文件
    for (const filePath of this.tempFiles) {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        this.log(`🗑️ 删除临时文件: ${filePath}`, 'info');
      }
    }
  }

  async validateBaseline() {
    this.log('\n🎯 验证基线 - 正常情况', 'info');
    
    const tests = [
      {
        name: '运行完整测试套件',
        command: 'cd frontend && npm run test:coverage',
        expectFailure: false
      },
      {
        name: '验证覆盖率达标',
        command: 'cd frontend && npm run test:coverage-verify',
        expectFailure: false
      },
      {
        name: '检查功能映射',
        command: 'cd frontend && npm run feature:validate',
        expectFailure: false
      }
    ];

    for (const test of tests) {
      this.log(`\n🧪 ${test.name}`, 'info');
      const result = await this.runCommand(test.command, test.expectFailure);
      this.results.push({
        category: 'baseline',
        test: test.name,
        passed: result.expected,
        output: result.output
      });
    }
  }

  async validateCoverageThresholdTampering() {
    this.log('\n🎯 验证覆盖率阈值篡改检测', 'warning');
    
    const configPath = 'frontend/jest.config.coverage.js';
    this.backupFile(configPath);
    
    try {
      // 尝试降低覆盖率阈值
      if (fs.existsSync(configPath)) {
        let content = fs.readFileSync(configPath, 'utf8');
        content = content.replace(/90/g, '50'); // 将90%改为50%
        fs.writeFileSync(configPath, content);
        this.log('📝 临时修改覆盖率阈值从90%到50%', 'warning');
      }
      
      // 验证系统是否检测到篡改
      const result = await this.runCommand(
        'cd frontend && npm run test:coverage-verify', 
        true // 期望失败
      );
      
      this.results.push({
        category: 'anti-cheat',
        test: '覆盖率阈值篡改检测',
        passed: result.expected,
        output: result.output
      });
      
    } finally {
      this.restoreFile(configPath);
    }
  }

  async validateFeatureMappingBypass() {
    this.log('\n🎯 验证功能映射绕过检测', 'warning');
    
    const testFile = 'frontend/tests/temp-bypass-test.spec.js';
    
    // 创建没有功能映射的测试文件
    const testContent = `
// 这是一个尝试绕过功能映射的测试文件
describe('Bypass Test', () => {
  it('should work without feature mapping', () => {
    expect(true).toBe(true);
  });
});
`;
    
    this.createTempFile(testFile, testContent);
    
    try {
      // 尝试运行没有功能映射的测试
      const result = await this.runCommand(
        `cd frontend && npm test -- --testPathPattern=temp-bypass-test.spec.js`,
        true // 期望失败
      );
      
      this.results.push({
        category: 'anti-cheat',
        test: '功能映射绕过检测',
        passed: result.expected,
        output: result.output
      });
      
    } finally {
      // 临时文件会在cleanup中删除
    }
  }

  async validateTestSkipping() {
    this.log('\n🎯 验证测试跳过检测', 'warning');
    
    // 尝试只运行部分测试
    const result = await this.runCommand(
      'cd frontend && npm test -- --testPathPattern=nonexistent-pattern',
      false // 这个命令本身不会失败，但覆盖率会不足
    );
    
    // 然后验证覆盖率检查是否能检测到问题
    const coverageResult = await this.runCommand(
      'cd frontend && npm run test:coverage-verify',
      true // 期望失败，因为覆盖率不足
    );
    
    this.results.push({
      category: 'anti-cheat',
      test: '测试跳过检测',
      passed: coverageResult.expected,
      output: coverageResult.output
    });
  }

  async validateConfigTampering() {
    this.log('\n🎯 验证配置文件篡改检测', 'warning');
    
    const jestConfigPath = 'frontend/jest.config.js';
    this.backupFile(jestConfigPath);
    
    try {
      if (fs.existsSync(jestConfigPath)) {
        let content = fs.readFileSync(jestConfigPath, 'utf8');
        // 尝试禁用覆盖率收集
        content = content.replace('collectCoverage: true', 'collectCoverage: false');
        fs.writeFileSync(jestConfigPath, content);
        this.log('📝 临时禁用覆盖率收集', 'warning');
      }
      
      // 运行测试并验证是否检测到配置篡改
      const result = await this.runCommand(
        'cd frontend && npm run test:coverage-verify',
        true // 期望失败
      );
      
      this.results.push({
        category: 'anti-cheat',
        test: '配置文件篡改检测',
        passed: result.expected,
        output: result.output
      });
      
    } finally {
      this.restoreFile(jestConfigPath);
    }
  }

  async validateCIIntegrity() {
    this.log('\n🎯 验证CI完整性检查', 'info');
    
    const tests = [
      {
        name: '检查GitHub Actions配置',
        command: 'test -f .github/workflows/branch-protection.yml',
        expectFailure: false
      },
      {
        name: '验证分支保护配置',
        command: 'test -f .github/workflows/feature-map.yml',
        expectFailure: false
      },
      {
        name: '检查pre-commit配置',
        command: 'test -f .pre-commit-config.yaml',
        expectFailure: false
      }
    ];

    for (const test of tests) {
      const result = await this.runCommand(test.command, test.expectFailure);
      this.results.push({
        category: 'ci-integrity',
        test: test.name,
        passed: result.expected,
        output: result.output
      });
    }
  }

  generateReport() {
    this.log('\n📊 生成验证报告', 'info');
    
    const categories = {
      baseline: '基线验证',
      'anti-cheat': '防作弊检测',
      'ci-integrity': 'CI完整性'
    };
    
    let report = '# 防作弊系统验证报告\n\n';
    report += `生成时间: ${new Date().toISOString()}\n\n`;
    
    for (const [category, categoryName] of Object.entries(categories)) {
      const categoryResults = this.results.filter(r => r.category === category);
      const passed = categoryResults.filter(r => r.passed).length;
      const total = categoryResults.length;
      
      report += `## ${categoryName} (${passed}/${total})\n\n`;
      
      for (const result of categoryResults) {
        const status = result.passed ? '✅' : '❌';
        report += `${status} **${result.test}**\n`;
        if (result.output && result.output.length < 200) {
          report += `   \`${result.output.replace(/\n/g, ' ').trim()}\`\n`;
        }
        report += '\n';
      }
    }
    
    const totalPassed = this.results.filter(r => r.passed).length;
    const totalTests = this.results.length;
    const successRate = ((totalPassed / totalTests) * 100).toFixed(1);
    
    report += `## 总结\n\n`;
    report += `- 总测试数: ${totalTests}\n`;
    report += `- 通过数: ${totalPassed}\n`;
    report += `- 成功率: ${successRate}%\n\n`;
    
    if (successRate >= 90) {
      report += `🎉 **防作弊系统验证通过！**\n`;
    } else {
      report += `⚠️ **防作弊系统需要改进**\n`;
    }
    
    const reportPath = 'demo/anti-cheat-validation-report.md';
    fs.writeFileSync(reportPath, report);
    this.log(`📄 报告已生成: ${reportPath}`, 'success');
    
    return { totalPassed, totalTests, successRate };
  }

  async run() {
    try {
      this.log('🚀 开始防作弊系统验证', 'info');
      
      await this.validateBaseline();
      await this.validateCoverageThresholdTampering();
      await this.validateFeatureMappingBypass();
      await this.validateTestSkipping();
      await this.validateConfigTampering();
      await this.validateCIIntegrity();
      
      const summary = this.generateReport();
      
      this.log('\n🎯 验证完成！', 'success');
      this.log(`成功率: ${summary.successRate}% (${summary.totalPassed}/${summary.totalTests})`, 'info');
      
      return summary.successRate >= 90;
      
    } catch (error) {
      this.log(`💥 验证过程出错: ${error.message}`, 'error');
      return false;
    } finally {
      this.cleanup();
    }
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  const validator = new AntiCheatValidator();
  
  validator.run().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('验证失败:', error);
    process.exit(1);
  });
}

module.exports = AntiCheatValidator;