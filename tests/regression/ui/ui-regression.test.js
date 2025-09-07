/**
 * UI回归测试套件
 * 用于检测UI界面的视觉回归问题
 */

const { test, expect } = require('@playwright/test');
const SnapshotManager = require('../utils/snapshot');
const config = require('../config/regression.config');
const pixelmatch = require('pixelmatch');
const { PNG } = require('pngjs');
const fs = require('fs').promises;
const path = require('path');

class UiRegressionTester {
  constructor(page) {
    this.page = page;
    this.snapshotManager = new SnapshotManager(config.snapshot);
    this.config = config.ui;
  }
  
  /**
   * 执行UI回归测试
   * @param {Object} testCase - 测试用例
   */
  async runUiTest(testCase) {
    const { name, url, selector, viewport, waitFor, actions } = testCase;
    
    console.log(`Running UI regression test: ${name}`);
    
    try {
      // 设置视口
      if (viewport) {
        await this.page.setViewportSize(viewport);
      }
      
      // 导航到页面
      await this.page.goto(url, { waitUntil: 'networkidle' });
      
      // 等待特定元素或时间
      if (waitFor) {
        if (typeof waitFor === 'string') {
          await this.page.waitForSelector(waitFor);
        } else if (typeof waitFor === 'number') {
          await this.page.waitForTimeout(waitFor);
        }
      }
      
      // 执行预定义动作
      if (actions && actions.length > 0) {
        await this.executeActions(actions);
      }
      
      // 隐藏动态元素
      await this.hideDynamicElements(testCase.hideDynamic);
      
      // 截图
      const screenshotOptions = {
        fullPage: testCase.fullPage || false,
        clip: testCase.clip,
        animations: 'disabled',
        caret: 'hide'
      };
      
      let screenshot;
      if (selector) {
        const element = await this.page.locator(selector);
        screenshot = await element.screenshot(screenshotOptions);
      } else {
        screenshot = await this.page.screenshot(screenshotOptions);
      }
      
      // 创建当前快照
      const currentSnapshot = await this.snapshotManager.createUiSnapshot(
        name,
        screenshot,
        {
          url,
          viewport: await this.page.viewportSize(),
          browser: this.page.context().browser().browserType().name(),
          selector,
          timestamp: new Date().toISOString()
        }
      );
      
      // 获取基线快照
      const baseline = await this.snapshotManager.getBaseline(name, 'ui');
      
      if (!baseline) {
        console.log(`No baseline found for ${name}, creating new baseline`);
        await this.snapshotManager.updateBaseline(name, currentSnapshot, 'ui');
        return {
          status: 'baseline_created',
          message: `Baseline created for ${name}`,
          snapshot: currentSnapshot
        };
      }
      
      // 执行视觉比较
      const comparisonResult = await this.compareScreenshots(
        baseline,
        currentSnapshot,
        testCase
      );
      
      return {
        status: comparisonResult.passed ? 'passed' : 'failed',
        message: comparisonResult.message,
        differences: comparisonResult.differences,
        diffImage: comparisonResult.diffImage,
        baseline,
        current: currentSnapshot
      };
      
    } catch (error) {
      throw new Error(`UI test failed: ${error.message}`);
    }
  }
  
  /**
   * 执行预定义动作
   * @param {Array} actions - 动作列表
   */
  async executeActions(actions) {
    for (const action of actions) {
      switch (action.type) {
        case 'click':
          await this.page.click(action.selector);
          break;
        case 'fill':
          await this.page.fill(action.selector, action.value);
          break;
        case 'hover':
          await this.page.hover(action.selector);
          break;
        case 'scroll':
          await this.page.evaluate((options) => {
            window.scrollTo(options.x || 0, options.y || 0);
          }, action.options || {});
          break;
        case 'wait':
          if (action.selector) {
            await this.page.waitForSelector(action.selector);
          } else {
            await this.page.waitForTimeout(action.timeout || 1000);
          }
          break;
        case 'select':
          await this.page.selectOption(action.selector, action.value);
          break;
        default:
          console.warn(`Unknown action type: ${action.type}`);
      }
      
      // 动作间等待
      if (action.wait) {
        await this.page.waitForTimeout(action.wait);
      }
    }
  }
  
  /**
   * 隐藏动态元素
   * @param {Array} selectors - 要隐藏的元素选择器
   */
  async hideDynamicElements(selectors = []) {
    // 默认隐藏的动态元素
    const defaultSelectors = [
      '[data-testid="timestamp"]',
      '.timestamp',
      '.loading',
      '.spinner',
      '[data-dynamic="true"]'
    ];
    
    const allSelectors = [...defaultSelectors, ...selectors];
    
    for (const selector of allSelectors) {
      try {
        await this.page.evaluate((sel) => {
          const elements = document.querySelectorAll(sel);
          elements.forEach(el => {
            el.style.visibility = 'hidden';
          });
        }, selector);
      } catch (error) {
        // 忽略选择器不存在的错误
      }
    }
  }
  
  /**
   * 比较截图
   * @param {Object} baseline - 基线快照
   * @param {Object} current - 当前快照
   * @param {Object} testCase - 测试用例
   */
  async compareScreenshots(baseline, current, testCase) {
    try {
      // 读取基线图片
      const baselineImagePath = path.join(
        this.snapshotManager.config.baselineDir,
        path.basename(baseline.imagePath || '')
      );
      
      const baselineBuffer = await fs.readFile(baselineImagePath);
      const currentBuffer = await fs.readFile(current.imagePath);
      
      // 解析PNG
      const baselineImg = PNG.sync.read(baselineBuffer);
      const currentImg = PNG.sync.read(currentBuffer);
      
      // 检查尺寸
      if (baselineImg.width !== currentImg.width || baselineImg.height !== currentImg.height) {
        return {
          passed: false,
          message: `Image dimensions changed: ${baselineImg.width}x${baselineImg.height} -> ${currentImg.width}x${currentImg.height}`,
          differences: [{
            type: 'dimension',
            expected: `${baselineImg.width}x${baselineImg.height}`,
            actual: `${currentImg.width}x${currentImg.height}`,
            severity: 'high'
          }]
        };
      }
      
      // 创建差异图片
      const { width, height } = baselineImg;
      const diffImg = new PNG({ width, height });
      
      // 执行像素比较
      const threshold = testCase.threshold || this.config.threshold || 0.1;
      const diffPixels = pixelmatch(
        baselineImg.data,
        currentImg.data,
        diffImg.data,
        width,
        height,
        {
          threshold,
          includeAA: false,
          alpha: 0.1,
          aaColor: [255, 255, 0],
          diffColor: [255, 0, 0],
          diffColorAlt: [0, 255, 0]
        }
      );
      
      const totalPixels = width * height;
      const diffPercentage = (diffPixels / totalPixels) * 100;
      const maxDiffPercentage = testCase.maxDiffPercentage || this.config.maxDiffPercentage || 1;
      
      // 保存差异图片
      let diffImagePath = null;
      if (diffPixels > 0) {
        diffImagePath = path.join(
          this.snapshotManager.config.snapshotDir,
          `${testCase.name}_diff_${Date.now()}.png`
        );
        await fs.writeFile(diffImagePath, PNG.sync.write(diffImg));
      }
      
      const passed = diffPercentage <= maxDiffPercentage;
      
      return {
        passed,
        message: passed 
          ? `UI regression test passed for ${testCase.name} (${diffPercentage.toFixed(2)}% difference)`
          : `UI regression detected for ${testCase.name}: ${diffPercentage.toFixed(2)}% difference (threshold: ${maxDiffPercentage}%)`,
        differences: passed ? [] : [{
          type: 'visual',
          diffPixels,
          diffPercentage: diffPercentage.toFixed(2),
          threshold: maxDiffPercentage,
          severity: diffPercentage > maxDiffPercentage * 2 ? 'high' : 'medium'
        }],
        diffImage: diffImagePath,
        stats: {
          totalPixels,
          diffPixels,
          diffPercentage: diffPercentage.toFixed(2)
        }
      };
      
    } catch (error) {
      throw new Error(`Screenshot comparison failed: ${error.message}`);
    }
  }
  
  /**
   * 批量运行UI回归测试
   * @param {Array} testCases - 测试用例数组
   */
  async runBatchTests(testCases) {
    const results = [];
    
    for (const testCase of testCases) {
      try {
        const result = await this.runUiTest(testCase);
        results.push({
          testCase: testCase.name,
          ...result
        });
      } catch (error) {
        results.push({
          testCase: testCase.name,
          status: 'error',
          message: error.message,
          error: error.stack
        });
      }
    }
    
    return results;
  }
  
  /**
   * 生成测试报告
   * @param {Array} results - 测试结果
   */
  generateReport(results) {
    const summary = {
      total: results.length,
      passed: results.filter(r => r.status === 'passed').length,
      failed: results.filter(r => r.status === 'failed').length,
      errors: results.filter(r => r.status === 'error').length,
      baselines: results.filter(r => r.status === 'baseline_created').length
    };
    
    const report = {
      timestamp: new Date().toISOString(),
      summary,
      results,
      config: this.config
    };
    
    return report;
  }
}

// Playwright测试套件
const testCases = config.ui.pages || [];

testCases.forEach(testCase => {
  test(`UI Regression: ${testCase.name}`, async ({ page }) => {
    const tester = new UiRegressionTester(page);
    
    const result = await tester.runUiTest(testCase);
    
    if (result.status === 'failed') {
      console.error('Visual regression detected:', result.differences);
      
      if (result.diffImage) {
        console.log(`Diff image saved: ${result.diffImage}`);
      }
      
      // 根据严重程度决定是否失败
      const criticalIssues = result.differences.filter(
        diff => diff.severity === 'high'
      );
      
      if (criticalIssues.length > 0) {
        throw new Error(result.message);
      } else {
        console.warn('Non-critical visual differences detected:', result.differences);
      }
    }
    
    expect(result.status).toMatch(/passed|baseline_created/);
  });
});

// 响应式测试
test('UI Responsive Regression', async ({ page }) => {
  const responsiveTests = testCases.filter(tc => tc.responsive);
  
  if (responsiveTests.length === 0) {
    console.log('No responsive tests configured');
    return;
  }
  
  const viewports = [
    { width: 1920, height: 1080, name: 'desktop' },
    { width: 1024, height: 768, name: 'tablet' },
    { width: 375, height: 667, name: 'mobile' }
  ];
  
  for (const testCase of responsiveTests) {
    for (const viewport of viewports) {
      const responsiveTestCase = {
        ...testCase,
        name: `${testCase.name}_${viewport.name}`,
        viewport: { width: viewport.width, height: viewport.height }
      };
      
      const tester = new UiRegressionTester(page);
      const result = await tester.runUiTest(responsiveTestCase);
      
      if (result.status === 'failed') {
        const criticalIssues = result.differences.filter(
          diff => diff.severity === 'high'
        );
        
        if (criticalIssues.length > 0) {
          throw new Error(`Responsive regression in ${viewport.name}: ${result.message}`);
        }
      }
    }
  }
});

// 跨浏览器测试（如果配置了多个浏览器）
test('UI Cross-browser Regression', async ({ page, browserName }) => {
  const crossBrowserTests = testCases.filter(tc => tc.crossBrowser);
  
  if (crossBrowserTests.length === 0) {
    console.log('No cross-browser tests configured');
    return;
  }
  
  for (const testCase of crossBrowserTests) {
    const browserTestCase = {
      ...testCase,
      name: `${testCase.name}_${browserName}`
    };
    
    const tester = new UiRegressionTester(page);
    const result = await tester.runUiTest(browserTestCase);
    
    if (result.status === 'failed') {
      const criticalIssues = result.differences.filter(
        diff => diff.severity === 'high'
      );
      
      if (criticalIssues.length > 0) {
        throw new Error(`Cross-browser regression in ${browserName}: ${result.message}`);
      }
    }
  }
});

module.exports = UiRegressionTester;