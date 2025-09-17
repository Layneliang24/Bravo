import { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';
import { glob } from 'glob';
import * as archiver from 'archiver';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Playwright 全局拆卸
 * 在所有测试运行完成后执行的清理操作
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 开始全局拆卸...');

  try {
    // 1. 生成测试报告摘要
    await generateTestSummary();

    // 2. 清理临时文件
    await cleanupTempFiles();

    // 3. 收集测试覆盖率
    await collectCoverage();

    // 4. 压缩测试结果
    await compressTestResults();

    // 5. 发送通知（如果配置了）
    await sendNotifications();

    // 6. 清理测试数据
    await cleanupTestData();

    console.log('✅ 全局拆卸完成');
  } catch (error) {
    console.error('❌ 全局拆卸失败:', error);
    // 不抛出错误，避免影响测试结果
  }
}

/**
 * 生成测试报告摘要
 */
async function generateTestSummary() {
  console.log('📊 生成测试报告摘要...');

  try {
    const testResultsPath = path.join(__dirname, 'test-results.json');

    if (fs.existsSync(testResultsPath)) {
      const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8'));

      const summary = {
        timestamp: new Date().toISOString(),
        total: testResults.stats?.total || 0,
        passed: testResults.stats?.passed || 0,
        failed: testResults.stats?.failed || 0,
        skipped: testResults.stats?.skipped || 0,
        duration: testResults.stats?.duration || 0,
        environment: {
          nodeVersion: process.version,
          platform: process.platform,
          arch: process.arch,
          baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3001',
          ci: !!process.env.CI,
        },
        browsers: testResults.config?.projects?.map((p: any) => p.name) || [],
        failedTests:
          testResults.suites?.flatMap(
            (suite: any) =>
              suite.specs
                ?.filter((spec: any) => spec.tests?.some((test: any) => test.status === 'failed'))
                .map((spec: any) => ({
                  title: spec.title,
                  file: spec.file,
                  errors: spec.tests
                    ?.filter((test: any) => test.status === 'failed')
                    .map((test: any) => test.error?.message),
                }))
          ) || [],
      };

      const summaryPath = path.join(__dirname, 'test-summary.json');
      fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

      // 生成人类可读的摘要
      const readableSummary = generateReadableSummary(summary);
      const readableSummaryPath = path.join(__dirname, 'test-summary.md');
      fs.writeFileSync(readableSummaryPath, readableSummary);

      console.log('  ✓ 测试摘要已生成');
      console.log(
        `  📈 总计: ${summary.total}, 通过: ${summary.passed}, 失败: ${summary.failed}, 跳过: ${summary.skipped}`
      );
    } else {
      console.log('  ⚠️  未找到测试结果文件');
    }
  } catch (error) {
    console.error('  ❌ 生成测试摘要失败:', error);
  }
}

/**
 * 生成人类可读的测试摘要
 */
function generateReadableSummary(summary: any): string {
  const passRate = summary.total > 0 ? ((summary.passed / summary.total) * 100).toFixed(2) : '0';
  const duration = (summary.duration / 1000).toFixed(2);

  return `# 测试报告摘要

## 📊 测试统计

- **总测试数**: ${summary.total}
- **通过**: ${summary.passed} ✅
- **失败**: ${summary.failed} ❌
- **跳过**: ${summary.skipped} ⏭️
- **通过率**: ${passRate}%
- **执行时间**: ${duration}秒

## 🌐 测试环境

- **Node.js版本**: ${summary.environment.nodeVersion}
- **平台**: ${summary.environment.platform}
- **架构**: ${summary.environment.arch}
- **基础URL**: ${summary.environment.baseUrl}
- **CI环境**: ${summary.environment.ci ? '是' : '否'}

## 🌍 测试浏览器

${summary.browsers.map((browser: string) => `- ${browser}`).join('\n')}

${
  summary.failedTests.length > 0
    ? `## ❌ 失败的测试

${summary.failedTests
  .map(
    (test: any) => `### ${test.title}

**文件**: ${test.file}

**错误**:
${test.errors.map((error: string) => `- ${error}`).join('\n')}
`
  )
  .join('\n')}`
    : '## ✅ 所有测试都通过了！'
}

---

*报告生成时间: ${new Date(summary.timestamp).toLocaleString('zh-CN')}*
`;
}

/**
 * 清理临时文件
 */
async function cleanupTempFiles() {
  console.log('🗑️  清理临时文件...');

  const tempFiles = ['auth.json', '.tmp', 'temp', '*.tmp', '*.temp'];

  for (const pattern of tempFiles) {
    try {
      const files = pattern.includes('*') ? glob.sync(pattern, { cwd: __dirname }) : [pattern];

      for (const file of files) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
          const stat = fs.statSync(filePath);
          if (stat.isDirectory()) {
            fs.rmSync(filePath, { recursive: true, force: true });
          } else {
            fs.unlinkSync(filePath);
          }
          console.log(`  ✓ 已删除 ${file}`);
        }
      }
    } catch (error) {
      console.log(`  ⚠️  清理 ${pattern} 失败:`, (error as Error).message);
    }
  }
}

/**
 * 收集测试覆盖率
 */
async function collectCoverage() {
  console.log('📈 收集测试覆盖率...');

  try {
    // 检查是否有覆盖率数据
    const coverageDir = path.join(__dirname, 'coverage');

    if (fs.existsSync(coverageDir)) {
      // 合并覆盖率报告
      const coverageFiles = fs
        .readdirSync(coverageDir)
        .filter(file => file.endsWith('.json'))
        .map(file => path.join(coverageDir, file));

      if (coverageFiles.length > 0) {
        console.log(`  ✓ 找到 ${coverageFiles.length} 个覆盖率文件`);

        // 这里可以添加覆盖率合并逻辑
        // 例如使用 nyc 或其他工具合并覆盖率报告

        // 生成覆盖率摘要
        const coverageSummary = {
          timestamp: new Date().toISOString(),
          files: coverageFiles.length,
          // 这里可以添加更多覆盖率统计信息
        };

        const summaryPath = path.join(coverageDir, 'summary.json');
        fs.writeFileSync(summaryPath, JSON.stringify(coverageSummary, null, 2));

        console.log('  ✓ 覆盖率摘要已生成');
      } else {
        console.log('  ℹ️  未找到覆盖率数据');
      }
    } else {
      console.log('  ℹ️  覆盖率目录不存在');
    }
  } catch (error) {
    console.error('  ❌ 收集覆盖率失败:', error);
  }
}

/**
 * 压缩测试结果
 */
async function compressTestResults() {
  console.log('🗜️  压缩测试结果...');

  try {
    // archiver已在顶部导入
    const output = fs.createWriteStream(path.join(__dirname, 'test-results.zip'));
    const archive = archiver.create('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      console.log(`  ✓ 测试结果已压缩 (${archive.pointer()} bytes)`);
    });

    archive.on('error', (err: any) => {
      throw err;
    });

    archive.pipe(output);

    // 添加测试结果目录
    const dirsToArchive = ['test-results', 'playwright-report', 'coverage', 'screenshots'];

    for (const dir of dirsToArchive) {
      const dirPath = path.join(__dirname, dir);
      if (fs.existsSync(dirPath)) {
        archive.directory(dirPath, dir);
      }
    }

    // 添加摘要文件
    const summaryFiles = ['test-summary.json', 'test-summary.md'];
    for (const file of summaryFiles) {
      const filePath = path.join(__dirname, file);
      if (fs.existsSync(filePath)) {
        archive.file(filePath, { name: file });
      }
    }

    await archive.finalize();
  } catch (error) {
    console.log('  ⚠️  压缩测试结果失败:', (error as Error).message);
  }
}

/**
 * 发送通知
 */
async function sendNotifications() {
  console.log('📢 发送通知...');

  try {
    // 检查是否配置了通知
    const webhookUrl = process.env.TEST_WEBHOOK_URL;
    const emailConfig = process.env.TEST_EMAIL_CONFIG;

    if (webhookUrl) {
      await sendWebhookNotification(webhookUrl);
    }

    if (emailConfig) {
      await sendEmailNotification(emailConfig);
    }

    if (!webhookUrl && !emailConfig) {
      console.log('  ℹ️  未配置通知方式');
    }
  } catch (error) {
    console.error('  ❌ 发送通知失败:', error);
  }
}

/**
 * 发送Webhook通知
 */
async function sendWebhookNotification(webhookUrl: string) {
  try {
    const summaryPath = path.join(__dirname, 'test-summary.json');
    if (fs.existsSync(summaryPath)) {
      const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));

      const payload = {
        text: `测试完成 - 通过: ${summary.passed}/${summary.total}`,
        summary: summary,
      };

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        console.log('  ✓ Webhook通知已发送');
      } else {
        console.log('  ⚠️  Webhook通知发送失败');
      }
    }
  } catch (error) {
    console.error('  ❌ Webhook通知失败:', error);
  }
}

/**
 * 发送邮件通知
 */
async function sendEmailNotification(emailConfig: string) {
  try {
    // 这里可以实现邮件发送逻辑
    console.log('  ℹ️  邮件通知功能待实现');
  } catch (error) {
    console.error('  ❌ 邮件通知失败:', error);
  }
}

/**
 * 清理测试数据
 */
async function cleanupTestData() {
  console.log('🗄️  清理测试数据...');

  try {
    // 清理测试数据库
    const testDbPath = path.join(__dirname, '../backend/test.db');
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
      console.log('  ✓ 已清理测试数据库');
    }

    // 清理测试上传文件
    const testUploadsPath = path.join(__dirname, '../backend/uploads/test');
    if (fs.existsSync(testUploadsPath)) {
      fs.rmSync(testUploadsPath, { recursive: true, force: true });
      console.log('  ✓ 已清理测试上传文件');
    }

    // 清理测试缓存
    const testCachePath = path.join(__dirname, '../backend/cache/test');
    if (fs.existsSync(testCachePath)) {
      fs.rmSync(testCachePath, { recursive: true, force: true });
      console.log('  ✓ 已清理测试缓存');
    }
  } catch (error) {
    console.error('  ❌ 清理测试数据失败:', error);
  }
}

export default globalTeardown;

// 导出辅助函数
export {
  generateTestSummary,
  cleanupTempFiles,
  collectCoverage,
  compressTestResults,
  sendNotifications,
  cleanupTestData,
};

// 环境变量说明
/*
可选的环境变量:
- TEST_WEBHOOK_URL: Webhook通知URL (如Slack、Teams等)
- TEST_EMAIL_CONFIG: 邮件配置JSON字符串
- KEEP_TEST_DATA: 设置为'true'时保留测试数据
- COMPRESS_RESULTS: 设置为'false'时跳过结果压缩
*/
