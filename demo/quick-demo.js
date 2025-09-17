#!/usr/bin/env node
/**
 * 防作弊系统快速演示脚本
 * 展示关键检测点的工作原理
 */

const fs = require("fs");
const path = require("path");

// 模拟颜色输出
const colors = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`,
};

class QuickDemo {
  constructor() {
    this.checks = [];
  }

  log(message, color = "blue") {
    // eslint-disable-next-line no-console
    console.log(colors[color](message));
  }

  addCheck(name, result, details) {
    this.checks.push({ name, result, details });
    const status = result ? "✅" : "❌";
    const statusColor = result ? "green" : "red";
    this.log(`${status} ${name}`, statusColor);
    if (details) {
      this.log(`   ${details}`, "yellow");
    }
  }

  checkFileExists(filePath, description) {
    const exists = fs.existsSync(filePath);
    this.addCheck(
      description,
      exists,
      exists ? `文件存在: ${filePath}` : `文件缺失: ${filePath}`,
    );
    return exists;
  }

  checkConfigContent(filePath, searchText, description) {
    if (!fs.existsSync(filePath)) {
      this.addCheck(description, false, `配置文件不存在: ${filePath}`);
      return false;
    }

    const content = fs.readFileSync(filePath, "utf8");
    const hasContent = content.includes(searchText);
    this.addCheck(
      description,
      hasContent,
      hasContent ? `找到配置: ${searchText}` : `缺少配置: ${searchText}`,
    );
    return hasContent;
  }

  simulateCheatAttempt(cheatType, detectionMethod) {
    this.log(`\n🎭 模拟作弊尝试: ${cheatType}`, "yellow");

    // 模拟检测逻辑
    const detected = true; // 在实际系统中，这里会是真实的检测逻辑

    this.addCheck(`检测${cheatType}`, detected, `检测方法: ${detectionMethod}`);

    return detected;
  }

  demonstrateFeatureMapping() {
    this.log("\n🎯 功能映射系统演示", "bold");

    // 检查功能清单
    const featuresExist = this.checkFileExists(
      "features.json",
      "功能清单文件存在",
    );

    if (featuresExist) {
      try {
        const features = JSON.parse(fs.readFileSync("features.json", "utf8"));
        this.addCheck(
          "功能清单格式正确",
          Array.isArray(features),
          `包含 ${features.length} 个功能`,
        );

        // 检查功能ID格式
        const validIds = features.every(
          (f) => f.id && f.id.match(/^[A-Z]+-\d{3}$/),
        );
        this.addCheck(
          "功能ID格式规范",
          validIds,
          "所有功能ID符合 XXX-001 格式",
        );
      } catch (error) {
        this.addCheck("功能清单解析", false, `JSON格式错误: ${error.message}`);
      }
    }

    // 检查映射系统文件
    this.checkFileExists("testMap.js", "测试映射核心文件存在");

    this.checkFileExists("matchFeatures.js", "功能匹配器文件存在");
  }

  demonstrateCoverageProtection() {
    this.log("\n🛡️ 覆盖率保护演示", "bold");

    // 检查Jest配置
    this.checkConfigContent(
      "frontend/jest.config.js",
      "collectCoverage: true",
      "Jest覆盖率收集已启用",
    );

    this.checkConfigContent(
      "frontend/jest.config.coverage.js",
      "90",
      "覆盖率阈值设置为90%",
    );

    // 检查验证脚本
    this.checkFileExists(
      "frontend/tests/verify-coverage.js",
      "覆盖率验证脚本存在",
    );

    // 模拟阈值篡改检测
    this.simulateCheatAttempt(
      "降低覆盖率阈值",
      "verify-coverage.js中的硬编码检查",
    );
  }

  demonstrateCIProtection() {
    this.log("\n🔒 CI保护机制演示", "bold");

    // 检查GitHub Actions配置
    this.checkFileExists(
      ".github/workflows/branch-protection.yml",
      "分支保护工作流存在",
    );

    this.checkFileExists(
      ".github/workflows/feature-map.yml",
      "功能映射工作流存在",
    );

    // 检查分支保护配置内容
    this.checkConfigContent(
      ".github/workflows/branch-protection.yml",
      "npm run test:coverage",
      "CI强制运行覆盖率测试",
    );

    this.checkConfigContent(
      ".github/workflows/branch-protection.yml",
      "npm run feature:validate",
      "CI强制验证功能映射",
    );

    // 模拟CI绕过尝试
    this.simulateCheatAttempt("绕过CI检查", "GitHub分支保护规则强制执行");
  }

  demonstrateTestIntegrity() {
    this.log("\n🧪 测试完整性演示", "bold");

    // 检查测试示例文件
    this.checkFileExists(
      "frontend/tests/examples/feature-mapping-demo.test.js",
      "功能映射示例测试存在",
    );

    // 检查测试配置
    this.checkConfigContent(
      "frontend/jest.config.js",
      "setupFilesAfterEnv",
      "测试环境设置已配置",
    );

    // 模拟测试跳过检测
    this.simulateCheatAttempt("跳过部分测试", "CI中的全量测试强制执行");

    // 模拟功能映射绕过
    this.simulateCheatAttempt("绕过功能映射", "matchFeatures.js中的强制验证");
  }

  generateSummary() {
    this.log("\n📊 演示总结", "bold");

    const totalChecks = this.checks.length;
    const passedChecks = this.checks.filter((c) => c.result).length;
    const successRate = ((passedChecks / totalChecks) * 100).toFixed(1);

    this.log(`总检查项: ${totalChecks}`);
    this.log(`通过项: ${passedChecks}`);
    this.log(`成功率: ${successRate}%`);

    if (successRate >= 90) {
      this.log("\n🎉 防作弊系统配置完整！", "green");
    } else {
      this.log("\n⚠️ 防作弊系统需要完善", "red");

      const failedChecks = this.checks.filter((c) => !c.result);
      this.log("\n失败的检查项:", "red");
      failedChecks.forEach((check) => {
        this.log(`  - ${check.name}: ${check.details}`, "red");
      });
    }

    return { totalChecks, passedChecks, successRate };
  }

  run() {
    this.log("🚀 防作弊系统快速演示开始", "bold");
    this.log("=".repeat(50), "blue");

    this.demonstrateFeatureMapping();
    this.demonstrateCoverageProtection();
    this.demonstrateCIProtection();
    this.demonstrateTestIntegrity();

    const summary = this.generateSummary();

    this.log("\n" + "=".repeat(50), "blue");
    this.log("演示完成！", "bold");

    return summary;
  }
}

// 运行演示
if (require.main === module) {
  const demo = new QuickDemo();
  const result = demo.run();

  // 根据结果设置退出码
  process.exit(result.successRate >= 90 ? 0 : 1);
}

module.exports = QuickDemo;
