const fs = require("fs");
const path = require("path");

// 功能-测试映射存储
const featureTestMap = new Map();
const testFeatureMap = new Map();

// 加载功能清单
function loadFeatures() {
  try {
    const featuresPath = path.join(process.cwd(), "features.json");
    const featuresData = fs.readFileSync(featuresPath, "utf8");
    return JSON.parse(featuresData);
  } catch (error) {
    console.warn("Warning: Could not load features.json:", error.message);
    return [];
  }
}

// 验证功能ID是否存在
function validateFeatureId(featureId) {
  const features = loadFeatures();
  const validIds = features.map((f) => f.id);

  if (!validIds.includes(featureId)) {
    throw new Error(
      `Invalid feature ID: ${featureId}. Valid IDs: ${validIds.join(", ")}`,
    );
  }

  return true;
}

// 链接测试到功能
function linkTestToFeature(featureId, testFile = null) {
  // 获取调用栈信息来确定测试文件
  if (!testFile) {
    const stack = new Error().stack;
    const stackLines = stack.split("\n");

    // 查找测试文件路径
    for (let line of stackLines) {
      if (line.includes(".test.") || line.includes(".spec.")) {
        const match = line.match(/\(([^)]+)\)/);
        if (match) {
          testFile = path.relative(process.cwd(), match[1].split(":")[0]);
          break;
        }
      }
    }
  }

  if (!testFile) {
    throw new Error(
      "Could not determine test file. Please provide testFile parameter.",
    );
  }

  // 验证功能ID
  validateFeatureId(featureId);

  // 建立双向映射
  if (!featureTestMap.has(featureId)) {
    featureTestMap.set(featureId, new Set());
  }
  featureTestMap.get(featureId).add(testFile);

  if (!testFeatureMap.has(testFile)) {
    testFeatureMap.set(testFile, new Set());
  }
  testFeatureMap.get(testFile).add(featureId);

  // 在CI环境下记录映射关系
  if (process.env.CI) {
    const mappingFile = path.join(process.cwd(), "feature-test-mapping.json");
    const mapping = {
      featureId,
      testFile,
      timestamp: new Date().toISOString(),
      testSuite: process.env.JEST_WORKER_ID || "unknown",
    };

    // 追加到映射文件
    try {
      let existingMappings = [];
      if (fs.existsSync(mappingFile)) {
        existingMappings = JSON.parse(fs.readFileSync(mappingFile, "utf8"));
      }
      existingMappings.push(mapping);
      fs.writeFileSync(mappingFile, JSON.stringify(existingMappings, null, 2));
    } catch (error) {
      console.warn("Warning: Could not write feature mapping:", error.message);
    }
  }

  console.log(`✓ Linked test ${testFile} to feature ${featureId}`);
  return true;
}

// 获取功能的测试覆盖情况
function getFeatureCoverage(featureId = null) {
  const features = loadFeatures();

  if (featureId) {
    const feature = features.find((f) => f.id === featureId);
    if (!feature) {
      throw new Error(`Feature ${featureId} not found`);
    }

    return {
      feature,
      tests: Array.from(featureTestMap.get(featureId) || []),
      covered:
        featureTestMap.has(featureId) && featureTestMap.get(featureId).size > 0,
    };
  }

  // 返回所有功能的覆盖情况
  return features.map((feature) => ({
    feature,
    tests: Array.from(featureTestMap.get(feature.id) || []),
    covered:
      featureTestMap.has(feature.id) && featureTestMap.get(feature.id).size > 0,
  }));
}

// 获取测试文件覆盖的功能
function getTestCoverage(testFile) {
  const features = testFeatureMap.get(testFile) || new Set();
  return Array.from(features);
}

// 验证所有功能都有测试覆盖
function validateAllFeaturesCovered() {
  const features = loadFeatures();
  const uncoveredFeatures = [];

  for (const feature of features) {
    if (
      !featureTestMap.has(feature.id) ||
      featureTestMap.get(feature.id).size === 0
    ) {
      uncoveredFeatures.push(feature);
    }
  }

  if (uncoveredFeatures.length > 0) {
    const errorMsg = `Uncovered features found:\n${uncoveredFeatures
      .map((f) => `  - ${f.id}: ${f.desc}`)
      .join("\n")}`;
    throw new Error(errorMsg);
  }

  console.log(`✓ All ${features.length} features have test coverage`);
  return true;
}

// 生成覆盖报告
function generateCoverageReport() {
  const coverage = getFeatureCoverage();
  const totalFeatures = coverage.length;
  const coveredFeatures = coverage.filter((c) => c.covered).length;
  const coveragePercentage =
    totalFeatures > 0
      ? ((coveredFeatures / totalFeatures) * 100).toFixed(2)
      : 0;

  const report = {
    summary: {
      totalFeatures,
      coveredFeatures,
      uncoveredFeatures: totalFeatures - coveredFeatures,
      coveragePercentage: parseFloat(coveragePercentage),
    },
    details: coverage.map((c) => ({
      featureId: c.feature.id,
      description: c.feature.desc,
      category: c.feature.category,
      priority: c.feature.priority,
      covered: c.covered,
      testFiles: c.tests,
      testCount: c.tests.length,
    })),
    uncovered: coverage
      .filter((c) => !c.covered)
      .map((c) => ({
        featureId: c.feature.id,
        description: c.feature.desc,
        category: c.feature.category,
        priority: c.feature.priority,
      })),
    timestamp: new Date().toISOString(),
  };

  return report;
}

// 导出函数
module.exports = {
  linkTestToFeature,
  getFeatureCoverage,
  getTestCoverage,
  validateAllFeaturesCovered,
  generateCoverageReport,
  validateFeatureId,
  loadFeatures,
};

// Jest全局设置
if (typeof global !== "undefined" && global.beforeAll) {
  // 在测试开始前清理映射
  global.beforeAll(() => {
    featureTestMap.clear();
    testFeatureMap.clear();
  });

  // 在所有测试结束后验证覆盖率
  global.afterAll(() => {
    if (process.env.VALIDATE_FEATURE_COVERAGE === "true") {
      try {
        validateAllFeaturesCovered();
      } catch (error) {
        console.error("Feature coverage validation failed:", error.message);
        process.exit(1);
      }
    }
  });
}
