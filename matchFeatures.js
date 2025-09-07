const { linkTestToFeature, validateFeatureId, loadFeatures } = require('./testMap');

// 全局功能映射配置
global.linkTestToFeature = linkTestToFeature;
global.validateFeatureId = validateFeatureId;
global.loadFeatures = loadFeatures;

// Jest自定义匹配器
expect.extend({
  toHaveFeatureCoverage(received, featureId) {
    const { getFeatureCoverage } = require('./testMap');
    
    try {
      const coverage = getFeatureCoverage(featureId);
      const pass = coverage.covered && coverage.tests.length > 0;
      
      if (pass) {
        return {
          message: () => `Expected feature ${featureId} not to have test coverage, but it has ${coverage.tests.length} test(s)`,
          pass: true
        };
      } else {
        return {
          message: () => `Expected feature ${featureId} to have test coverage, but no tests found`,
          pass: false
        };
      }
    } catch (error) {
      return {
        message: () => `Feature coverage check failed: ${error.message}`,
        pass: false
      };
    }
  },
  
  toBeValidFeatureId(received) {
    try {
      validateFeatureId(received);
      return {
        message: () => `Expected ${received} not to be a valid feature ID`,
        pass: true
      };
    } catch (error) {
      return {
        message: () => `Expected ${received} to be a valid feature ID: ${error.message}`,
        pass: false
      };
    }
  }
});

// 测试文件模板验证
function validateTestFileStructure() {
  const testFile = expect.getState().testPath;
  if (!testFile) return;
  
  const fs = require('fs');
  const path = require('path');
  
  try {
    const content = fs.readFileSync(testFile, 'utf8');
    
    // 检查是否包含linkTestToFeature调用
    const hasFeatureLink = content.includes('linkTestToFeature(');
    
    if (!hasFeatureLink && process.env.ENFORCE_FEATURE_MAPPING === 'true') {
      console.warn(`⚠️  Test file ${path.relative(process.cwd(), testFile)} does not call linkTestToFeature()`);
      console.warn('   Add linkTestToFeature("FEATURE-ID") at the top of your test file.');
    }
  } catch (error) {
    // 忽略文件读取错误
  }
}

// 在每个测试套件开始前验证
beforeAll(() => {
  validateTestFileStructure();
});

// 功能映射助手函数
global.describeFeature = function(featureId, description, testFn) {
  // 验证功能ID
  try {
    validateFeatureId(featureId);
  } catch (error) {
    throw new Error(`Invalid feature ID in describeFeature: ${error.message}`);
  }
  
  // 自动链接功能
  linkTestToFeature(featureId);
  
  // 执行测试套件
  return describe(`[${featureId}] ${description}`, testFn);
};

// 功能相关的测试助手
global.itShouldImplement = function(featureId, testDescription, testFn) {
  return it(`should implement ${featureId}: ${testDescription}`, testFn);
};

// 批量功能映射
global.linkMultipleFeatures = function(featureIds) {
  if (!Array.isArray(featureIds)) {
    throw new Error('linkMultipleFeatures expects an array of feature IDs');
  }
  
  featureIds.forEach(featureId => {
    linkTestToFeature(featureId);
  });
};

// 功能覆盖率报告（在CI环境下）
if (process.env.CI) {
  afterAll(async () => {
    const { generateCoverageReport } = require('./testMap');
    const fs = require('fs');
    const path = require('path');
    
    try {
      const report = generateCoverageReport();
      const reportPath = path.join(process.cwd(), 'feature-coverage-report.json');
      
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
      console.log(`📊 Feature coverage report generated: ${reportPath}`);
      console.log(`📈 Coverage: ${report.summary.coveragePercentage}% (${report.summary.coveredFeatures}/${report.summary.totalFeatures})`);
      
      if (report.summary.uncoveredFeatures > 0) {
        console.log('❌ Uncovered features:');
        report.uncovered.forEach(feature => {
          console.log(`   - ${feature.featureId}: ${feature.description}`);
        });
      }
    } catch (error) {
      console.error('Failed to generate feature coverage report:', error.message);
    }
  });
}

// 导出配置
module.exports = {
  linkTestToFeature,
  validateFeatureId,
  loadFeatures
};