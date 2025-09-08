#!/usr/bin/env node

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

/**
 * 检查TypeScript语法错误的脚本
 */
function checkSyntax() {
  console.log("🔍 检查TypeScript语法错误...");

  const errors = [];

  // 检查前端文件
  try {
    console.log("📁 检查前端文件...");
    execSync("cd frontend && npx tsc --noEmit --skipLibCheck", {
      stdio: "pipe",
      cwd: path.resolve(__dirname, ".."),
    });
    console.log("✅ 前端文件语法检查通过");
  } catch (error) {
    console.log("❌ 前端文件存在语法错误:");
    console.log(error.stdout?.toString() || error.message);
    errors.push("frontend");
  }

  // 检查E2E测试文件
  try {
    console.log("📁 检查E2E测试文件...");
    const e2eConfigPath = path.resolve(__dirname, "..", "e2e/tsconfig.json");

    if (fs.existsSync(e2eConfigPath)) {
      execSync("npx tsc --noEmit --project e2e/tsconfig.json", {
        stdio: "pipe",
        cwd: path.resolve(__dirname, ".."),
      });
    }
    console.log("✅ E2E测试文件语法检查通过");
  } catch (error) {
    console.log("❌ E2E测试文件存在语法错误:");
    console.log(error.stdout?.toString() || error.message);
    errors.push("e2e");
  }

  if (errors.length > 0) {
    console.log(
      `\n❌ 发现 ${errors.length} 个模块存在语法错误: ${errors.join(", ")}`,
    );
    process.exit(1);
  } else {
    console.log("\n🎉 所有文件语法检查通过!");
  }
}

if (require.main === module) {
  checkSyntax();
}

module.exports = { checkSyntax };
