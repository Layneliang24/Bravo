#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const glob = require("glob");

// 配置
const CONFIG = {
  featuresFile: "features.json",
  testPatterns: [
    "frontend/**/*.test.{js,jsx,ts,tsx}",
    "frontend/**/*.spec.{js,jsx,ts,tsx}",
    "backend/**/*.test.py",
    "backend/**/test_*.py",
    "tests/**/*.test.{js,py}",
  ],
  outputFile: "feature-test-map.md",
  jsonOutputFile: "feature-test-map.json",
  mappingFile: "feature-test-mapping.json",
};

// 加载功能清单
function loadFeatures() {
  try {
    const featuresPath = path.join(process.cwd(), CONFIG.featuresFile);
    const featuresData = fs.readFileSync(featuresPath, "utf8");
    return JSON.parse(featuresData);
  } catch (error) {
    console.error(`❌ Failed to load ${CONFIG.featuresFile}:`, error.message);
    process.exit(1);
  }
}

// 查找所有测试文件
function findTestFiles() {
  const testFiles = [];

  for (const pattern of CONFIG.testPatterns) {
    try {
      const files = glob.sync(pattern, { cwd: process.cwd() });
      testFiles.push(...files);
    } catch (error) {
      console.warn(
        `⚠️  Failed to find files with pattern ${pattern}:`,
        error.message,
      );
    }
  }

  return [...new Set(testFiles)]; // 去重
}

// 解析测试文件中的功能映射
function parseTestFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf8");
    const featureIds = [];

    // 匹配 linkTestToFeature 调用
    const linkMatches = content.match(
      /linkTestToFeature\s*\(\s*['"`]([^'"`)]+)['"`]\s*\)/g,
    );
    if (linkMatches) {
      linkMatches.forEach((match) => {
        const idMatch = match.match(/['"`]([^'"`)]+)['"`]/);
        if (idMatch) {
          featureIds.push(idMatch[1]);
        }
      });
    }

    // 匹配 describeFeature 调用
    const describeMatches = content.match(
      /describeFeature\s*\(\s*['"`]([^'"`)]+)['"`]/g,
    );
    if (describeMatches) {
      describeMatches.forEach((match) => {
        const idMatch = match.match(/['"`]([^'"`)]+)['"`]/);
        if (idMatch) {
          featureIds.push(idMatch[1]);
        }
      });
    }

    // 匹配注释中的功能ID
    const commentMatches = content.match(/\/\*\*?\s*@covers\s+([A-Z]+-\d+)/g);
    if (commentMatches) {
      commentMatches.forEach((match) => {
        const idMatch = match.match(/([A-Z]+-\d+)/);
        if (idMatch) {
          featureIds.push(idMatch[1]);
        }
      });
    }

    return [...new Set(featureIds)]; // 去重
  } catch (error) {
    console.warn(`⚠️  Failed to parse ${filePath}:`, error.message);
    return [];
  }
}

// 加载运行时映射数据
function loadRuntimeMapping() {
  try {
    const mappingPath = path.join(process.cwd(), CONFIG.mappingFile);
    if (fs.existsSync(mappingPath)) {
      const mappingData = fs.readFileSync(mappingPath, "utf8");
      return JSON.parse(mappingData);
    }
  } catch (error) {
    console.warn(`⚠️  Failed to load runtime mapping:`, error.message);
  }
  return [];
}

// 构建功能-测试映射
function buildFeatureTestMap() {
  console.log("🔍 Building feature-test mapping...");

  const features = loadFeatures();
  const testFiles = findTestFiles();
  const runtimeMapping = loadRuntimeMapping();

  console.log(`📋 Found ${features.length} features`);
  console.log(`🧪 Found ${testFiles.length} test files`);
  console.log(`⚡ Found ${runtimeMapping.length} runtime mappings`);

  // 构建映射关系
  const featureTestMap = new Map();
  const testFeatureMap = new Map();

  // 初始化所有功能
  features.forEach((feature) => {
    featureTestMap.set(feature.id, {
      feature,
      tests: new Set(),
      staticTests: new Set(),
      runtimeTests: new Set(),
    });
  });

  // 解析静态测试文件
  testFiles.forEach((testFile) => {
    const featureIds = parseTestFile(testFile);

    featureIds.forEach((featureId) => {
      if (featureTestMap.has(featureId)) {
        featureTestMap.get(featureId).tests.add(testFile);
        featureTestMap.get(featureId).staticTests.add(testFile);
      } else {
        console.warn(`⚠️  Unknown feature ID ${featureId} in ${testFile}`);
      }

      if (!testFeatureMap.has(testFile)) {
        testFeatureMap.set(testFile, new Set());
      }
      testFeatureMap.get(testFile).add(featureId);
    });
  });

  // 添加运行时映射
  runtimeMapping.forEach((mapping) => {
    if (featureTestMap.has(mapping.featureId)) {
      featureTestMap.get(mapping.featureId).tests.add(mapping.testFile);
      featureTestMap.get(mapping.featureId).runtimeTests.add(mapping.testFile);
    }
  });

  return { featureTestMap, testFeatureMap, features, testFiles };
}

// 生成Markdown报告
function generateMarkdownReport(featureTestMap, features) {
  const lines = [];

  lines.push("# 功能-测试覆盖地图\n");
  lines.push(`生成时间: ${new Date().toLocaleString()}\n`);

  // 统计信息
  const totalFeatures = features.length;
  const coveredFeatures = Array.from(featureTestMap.values()).filter(
    (item) => item.tests.size > 0,
  ).length;
  const coveragePercentage =
    totalFeatures > 0
      ? ((coveredFeatures / totalFeatures) * 100).toFixed(2)
      : 0;

  lines.push("## 📊 覆盖率统计\n");
  lines.push(`- **总功能数**: ${totalFeatures}`);
  lines.push(`- **已覆盖**: ${coveredFeatures}`);
  lines.push(`- **未覆盖**: ${totalFeatures - coveredFeatures}`);
  lines.push(`- **覆盖率**: ${coveragePercentage}%\n`);

  // 按分类统计
  const categoryStats = {};
  features.forEach((feature) => {
    const category = feature.category || "unknown";
    if (!categoryStats[category]) {
      categoryStats[category] = { total: 0, covered: 0 };
    }
    categoryStats[category].total++;
    if (featureTestMap.get(feature.id).tests.size > 0) {
      categoryStats[category].covered++;
    }
  });

  lines.push("## 📈 分类覆盖率\n");
  lines.push("| 分类 | 总数 | 已覆盖 | 覆盖率 |");
  lines.push("|------|------|--------|--------|");

  Object.entries(categoryStats).forEach(([category, stats]) => {
    const percentage =
      stats.total > 0 ? ((stats.covered / stats.total) * 100).toFixed(1) : 0;
    lines.push(
      `| ${category} | ${stats.total} | ${stats.covered} | ${percentage}% |`,
    );
  });
  lines.push("");

  // 详细映射表
  lines.push("## 🗺️ 详细映射\n");
  lines.push("| 功能ID | 描述 | 分类 | 优先级 | 测试文件 | 状态 |");
  lines.push("|--------|------|------|--------|----------|------|");

  features.forEach((feature) => {
    const mapping = featureTestMap.get(feature.id);
    const testFiles = Array.from(mapping.tests);
    const status = testFiles.length > 0 ? "✅" : "❌ **无测试**";
    const testFilesList =
      testFiles.length > 0
        ? testFiles.map((f) => `\`${f}\``).join("<br>")
        : "—";

    lines.push(
      `| ${feature.id} | ${feature.desc} | ${feature.category || "N/A"} | ${
        feature.priority || "N/A"
      } | ${testFilesList} | ${status} |`,
    );
  });

  // 未覆盖功能
  const uncoveredFeatures = features.filter(
    (feature) => featureTestMap.get(feature.id).tests.size === 0,
  );
  if (uncoveredFeatures.length > 0) {
    lines.push("\n## ❌ 未覆盖功能\n");
    uncoveredFeatures.forEach((feature) => {
      lines.push(
        `- **${feature.id}**: ${feature.desc} (${feature.category || "N/A"}, ${
          feature.priority || "N/A"
        })`,
      );
    });
  }

  // 高优先级未覆盖
  const highPriorityUncovered = uncoveredFeatures.filter(
    (f) => f.priority === "high" || f.priority === "critical",
  );
  if (highPriorityUncovered.length > 0) {
    lines.push("\n## 🚨 高优先级未覆盖\n");
    highPriorityUncovered.forEach((feature) => {
      lines.push(`- **${feature.id}**: ${feature.desc} (${feature.priority})`);
    });
  }

  return lines.join("\n");
}

// 生成JSON报告
function generateJsonReport(
  featureTestMap,
  testFeatureMap,
  features,
  testFiles,
) {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalFeatures: features.length,
      totalTestFiles: testFiles.length,
      coveredFeatures: Array.from(featureTestMap.values()).filter(
        (item) => item.tests.size > 0,
      ).length,
      coveragePercentage: 0,
    },
    features: [],
    testFiles: [],
    uncovered: [],
  };

  report.summary.coveragePercentage =
    report.summary.totalFeatures > 0
      ? (report.summary.coveredFeatures / report.summary.totalFeatures) * 100
      : 0;

  // 功能详情
  features.forEach((feature) => {
    const mapping = featureTestMap.get(feature.id);
    const featureData = {
      ...feature,
      tests: Array.from(mapping.tests),
      staticTests: Array.from(mapping.staticTests),
      runtimeTests: Array.from(mapping.runtimeTests),
      covered: mapping.tests.size > 0,
      testCount: mapping.tests.size,
    };

    report.features.push(featureData);

    if (!featureData.covered) {
      report.uncovered.push({
        id: feature.id,
        desc: feature.desc,
        category: feature.category,
        priority: feature.priority,
      });
    }
  });

  // 测试文件详情
  testFiles.forEach((testFile) => {
    const features = Array.from(testFeatureMap.get(testFile) || []);
    report.testFiles.push({
      file: testFile,
      features,
      featureCount: features.length,
    });
  });

  return report;
}

// 主函数
function main() {
  try {
    console.log("🚀 Starting feature-test mapping generation...");

    const { featureTestMap, testFeatureMap, features, testFiles } =
      buildFeatureTestMap();

    // 生成Markdown报告
    const markdownReport = generateMarkdownReport(featureTestMap, features);
    fs.writeFileSync(CONFIG.outputFile, markdownReport);
    console.log(`📝 Markdown report generated: ${CONFIG.outputFile}`);

    // 生成JSON报告
    const jsonReport = generateJsonReport(
      featureTestMap,
      testFeatureMap,
      features,
      testFiles,
    );
    fs.writeFileSync(
      CONFIG.jsonOutputFile,
      JSON.stringify(jsonReport, null, 2),
    );
    console.log(`📊 JSON report generated: ${CONFIG.jsonOutputFile}`);

    // 输出到GitHub Actions Summary
    if (process.env.GITHUB_STEP_SUMMARY) {
      fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, markdownReport);
      console.log("📋 Report added to GitHub Actions Summary");
    }

    // 检查覆盖率
    const coveragePercentage = jsonReport.summary.coveragePercentage;
    console.log(`\n📈 Feature Coverage: ${coveragePercentage.toFixed(2)}%`);

    if (jsonReport.uncovered.length > 0) {
      console.log("\n❌ Uncovered features:");
      jsonReport.uncovered.forEach((feature) => {
        console.log(`   - ${feature.id}: ${feature.desc}`);
      });
    }

    // 在CI环境下检查最低覆盖率
    const minCoverage = parseFloat(process.env.MIN_FEATURE_COVERAGE || "80");
    if (process.env.CI && coveragePercentage < minCoverage) {
      console.error(
        `\n💥 Feature coverage ${coveragePercentage.toFixed(
          2,
        )}% is below minimum ${minCoverage}%`,
      );
      process.exit(1);
    }

    console.log("\n✅ Feature-test mapping completed successfully!");
  } catch (error) {
    console.error("💥 Failed to generate feature-test mapping:", error.message);
    process.exit(1);
  }
}

// 运行
if (require.main === module) {
  main();
}

module.exports = {
  buildFeatureTestMap,
  generateMarkdownReport,
  generateJsonReport,
  loadFeatures,
  findTestFiles,
};
