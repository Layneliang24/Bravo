#!/usr/bin/env node
/**
 * 防作弊系统实战演示
 * 模拟真实的作弊场景和检测机制
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

class RealWorldDemo {
  constructor() {
    this.backupFiles = new Map();
    this.results = [];
  }

  log(message, type = "info") {
    const colors = {
      info: "\x1b[36m",
      success: "\x1b[32m",
      error: "\x1b[31m",
      warning: "\x1b[33m",
      bold: "\x1b[1m",
      reset: "\x1b[0m",
    };

    const prefix = {
      info: "ℹ️",
      success: "✅",
      error: "❌",
      warning: "⚠️",
    };

    // eslint-disable-next-line no-console
    console.log(
      `${colors[type]}${prefix[type] || ""} ${message}${colors.reset}`,
    );
  }

  backupFile(filePath) {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf8");
      this.backupFiles.set(filePath, content);
      this.log(`备份文件: ${filePath}`, "info");
    }
  }

  restoreFile(filePath) {
    if (this.backupFiles.has(filePath)) {
      fs.writeFileSync(filePath, this.backupFiles.get(filePath));
      this.log(`恢复文件: ${filePath}`, "info");
    }
  }

  restoreAllFiles() {
    this.log("\n🔄 恢复所有文件...", "info");
    for (const filePath of this.backupFiles.keys()) {
      this.restoreFile(filePath);
    }
    this.backupFiles.clear();
  }

  runCommand(command, expectFailure = false) {
    try {
      const output = execSync(command, {
        encoding: "utf8",
        cwd: process.cwd(),
        stdio: "pipe",
      });

      if (expectFailure) {
        this.log(`命令意外成功: ${command}`, "warning");
        return { success: true, output };
      } else {
        this.log(`命令执行成功: ${command}`, "success");
        return { success: true, output };
      }
    } catch (error) {
      if (expectFailure) {
        this.log(`命令按预期失败: ${command}`, "success");
        return { success: false, error: error.message, expected: true };
      } else {
        this.log(`命令执行失败: ${command}`, "error");
        return { success: false, error: error.message, expected: false };
      }
    }
  }

  // 场景1: 尝试降低覆盖率阈值
  testCoverageThresholdTampering() {
    this.log("\n🎭 场景1: 尝试篡改覆盖率阈值", "bold");

    const configFile = "frontend/jest.config.coverage.js";
    this.backupFile(configFile);

    try {
      // 尝试将90%改为60%
      let content = fs.readFileSync(configFile, "utf8");
      const tamperedContent = content.replace(/90/g, "60");
      fs.writeFileSync(configFile, tamperedContent);

      this.log("已篡改覆盖率阈值: 90% → 60%", "warning");

      // 运行验证脚本
      const result = this.runCommand(
        "node frontend/tests/verify-coverage.js",
        true,
      );

      if (result.expected) {
        this.results.push({
          scenario: "覆盖率阈值篡改检测",
          status: "PASS",
          description: "系统成功检测到阈值篡改并阻止",
        });
      } else {
        this.results.push({
          scenario: "覆盖率阈值篡改检测",
          status: "FAIL",
          description: "系统未能检测到阈值篡改",
        });
      }
    } catch (error) {
      this.log(`测试执行错误: ${error.message}`, "error");
    } finally {
      this.restoreFile(configFile);
    }
  }

  // 场景2: 尝试跳过功能映射
  testFeatureMappingBypass() {
    this.log("\n🎭 场景2: 尝试绕过功能映射", "bold");

    const testFile = "frontend/tests/temp-bypass-test.js";

    try {
      // 创建一个没有功能映射的测试文件
      const bypassTestContent = `
describe('绕过测试', () => {
  it('应该通过但没有功能映射', () => {
    expect(1 + 1).toBe(2);
  });
});
`;

      fs.writeFileSync(testFile, bypassTestContent);
      this.log("创建了绕过功能映射的测试文件", "warning");

      // 尝试运行测试
      const result = this.runCommand(
        "cd frontend && npm run test:feature-mapping",
        true,
      );

      if (result.expected) {
        this.results.push({
          scenario: "功能映射绕过检测",
          status: "PASS",
          description: "系统成功检测到未映射的测试并阻止",
        });
      } else {
        this.results.push({
          scenario: "功能映射绕过检测",
          status: "FAIL",
          description: "系统未能检测到功能映射绕过",
        });
      }
    } catch (error) {
      this.log(`测试执行错误: ${error.message}`, "error");
    } finally {
      // 清理临时文件
      if (fs.existsSync(testFile)) {
        fs.unlinkSync(testFile);
        this.log("清理临时测试文件", "info");
      }
    }
  }

  // 场景3: 测试功能映射系统的正确使用
  testCorrectFeatureMapping() {
    this.log("\n🎭 场景3: 正确的功能映射使用", "bold");

    const testFile = "frontend/tests/temp-correct-test.js";

    try {
      // 创建一个正确映射功能的测试文件
      const correctTestContent = `
const { linkTestToFeature } = require('../../matchFeatures');

describe('正确映射测试', () => {
  beforeAll(() => {
    linkTestToFeature('ENG-001'); // 映射到英语学习功能
  });

  it('应该通过并正确映射功能', () => {
    expect(1 + 1).toBe(2);
  });
});
`;

      fs.writeFileSync(testFile, correctTestContent);
      this.log("创建了正确映射功能的测试文件", "info");

      // 运行测试验证
      const result = this.runCommand(
        "cd frontend && npm run test:feature-mapping",
        false,
      );

      if (result.success) {
        this.results.push({
          scenario: "正确功能映射验证",
          status: "PASS",
          description: "系统正确识别和验证了功能映射",
        });
      } else {
        this.results.push({
          scenario: "正确功能映射验证",
          status: "FAIL",
          description: "系统未能正确处理功能映射",
        });
      }
    } catch (error) {
      this.log(`测试执行错误: ${error.message}`, "error");
    } finally {
      // 清理临时文件
      if (fs.existsSync(testFile)) {
        fs.unlinkSync(testFile);
        this.log("清理临时测试文件", "info");
      }
    }
  }

  // 场景4: 测试CI配置完整性
  testCIIntegrity() {
    this.log("\n🎭 场景4: CI配置完整性检查", "bold");

    const workflowFile = ".github/workflows/branch-protection.yml";

    try {
      const content = fs.readFileSync(workflowFile, "utf8");

      // 检查关键配置项
      const checks = [
        { name: "强制覆盖率测试", pattern: "npm run test:coverage" },
        { name: "功能映射验证", pattern: "npm run feature:validate" },
        { name: "分支保护", pattern: 'branches: ["main", "dev"]' },
        { name: "测试失败阻止", pattern: "if: failure()" },
      ];

      let allPassed = true;

      checks.forEach((check) => {
        const found = content.includes(check.pattern);
        if (found) {
          this.log(`✓ ${check.name}: 配置正确`, "success");
        } else {
          this.log(`✗ ${check.name}: 配置缺失`, "error");
          allPassed = false;
        }
      });

      this.results.push({
        scenario: "CI配置完整性",
        status: allPassed ? "PASS" : "FAIL",
        description: allPassed ? "所有CI保护配置完整" : "部分CI配置缺失",
      });
    } catch (error) {
      this.log(`CI配置检查错误: ${error.message}`, "error");
      this.results.push({
        scenario: "CI配置完整性",
        status: "FAIL",
        description: `配置文件读取失败: ${error.message}`,
      });
    }
  }

  // 场景5: 功能清单完整性验证
  testFeatureListIntegrity() {
    this.log("\n🎭 场景5: 功能清单完整性验证", "bold");

    try {
      const features = JSON.parse(fs.readFileSync("features.json", "utf8"));

      const checks = [
        {
          name: "功能数量合理",
          test: () => features.length >= 10 && features.length <= 50,
          description: `当前有${features.length}个功能`,
        },
        {
          name: "ID格式规范",
          test: () =>
            features.every((f) => f.id && f.id.match(/^[A-Z]+-\d{3}$/)),
          description: "所有功能ID符合XXX-001格式",
        },
        {
          name: "优先级设置",
          test: () =>
            features.every((f) =>
              ["high", "medium", "low"].includes(f.priority),
            ),
          description: "所有功能都有有效的优先级",
        },
        {
          name: "描述完整",
          test: () =>
            features.every((f) => f.description && f.description.length > 10),
          description: "所有功能都有详细描述",
        },
      ];

      let allPassed = true;

      checks.forEach((check) => {
        const passed = check.test();
        if (passed) {
          this.log(`✓ ${check.name}: ${check.description}`, "success");
        } else {
          this.log(`✗ ${check.name}: 验证失败`, "error");
          allPassed = false;
        }
      });

      this.results.push({
        scenario: "功能清单完整性",
        status: allPassed ? "PASS" : "FAIL",
        description: allPassed ? "功能清单格式和内容完整" : "功能清单存在问题",
      });
    } catch (error) {
      this.log(`功能清单检查错误: ${error.message}`, "error");
      this.results.push({
        scenario: "功能清单完整性",
        status: "FAIL",
        description: `功能清单读取失败: ${error.message}`,
      });
    }
  }

  generateDetailedReport() {
    this.log("\n📊 详细测试报告", "bold");
    this.log("=".repeat(60), "info");

    const passed = this.results.filter((r) => r.status === "PASS").length;
    const total = this.results.length;
    const successRate = ((passed / total) * 100).toFixed(1);

    this.results.forEach((result, index) => {
      const status = result.status === "PASS" ? "✅" : "❌";
      this.log(`${index + 1}. ${status} ${result.scenario}`);
      this.log(`   ${result.description}`, "info");
    });

    this.log("\n" + "=".repeat(60), "info");
    this.log(`总测试场景: ${total}`, "info");
    this.log(`通过场景: ${passed}`, passed === total ? "success" : "warning");
    this.log(
      `成功率: ${successRate}%`,
      successRate >= 90 ? "success" : "error",
    );

    if (successRate >= 90) {
      this.log("\n🎉 防作弊系统运行良好！", "success");
      this.log("系统能够有效检测和阻止各种作弊尝试。", "success");
    } else {
      this.log("\n⚠️ 防作弊系统需要改进", "warning");
      this.log("建议检查失败的场景并完善相关配置。", "warning");
    }

    return { passed, total, successRate };
  }

  async run() {
    this.log("🚀 防作弊系统实战演示开始", "bold");
    this.log("本演示将模拟真实的作弊场景并验证检测能力", "info");

    try {
      // 运行所有测试场景
      this.testCoverageThresholdTampering();
      this.testFeatureMappingBypass();
      this.testCorrectFeatureMapping();
      this.testCIIntegrity();
      this.testFeatureListIntegrity();

      // 生成报告
      const report = this.generateDetailedReport();

      return report;
    } catch (error) {
      this.log(`演示执行错误: ${error.message}`, "error");
      return { passed: 0, total: 0, successRate: 0 };
    } finally {
      // 确保清理所有临时文件
      this.restoreAllFiles();
    }
  }
}

// 运行实战演示
if (require.main === module) {
  const demo = new RealWorldDemo();

  demo
    .run()
    .then((result) => {
      process.exit(result.successRate >= 80 ? 0 : 1);
    })
    .catch((error) => {
      console.error("演示运行失败:", error);
      process.exit(1);
    });
}

module.exports = RealWorldDemo;
