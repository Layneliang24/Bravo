/**
 * API回归测试套件
 * 用于检测API接口的回归问题
 */

const axios = require("axios");
const { expect } = require("@jest/globals");
const SnapshotManager = require("../utils/snapshot");
const config = require("../config/regression.config");

class ApiRegressionTester {
  constructor() {
    this.snapshotManager = new SnapshotManager(config.snapshot);
    this.baseUrl = config.api.baseUrl;
    this.timeout = config.api.timeout;
    this.retries = config.api.retries;
  }

  /**
   * 执行API回归测试
   * @param {Object} testCase - 测试用例
   */
  async runApiTest(testCase) {
    const { name, endpoint, method, headers, body, expectedStatus } = testCase;

    console.log(`Running API regression test: ${name}`);

    let response;
    let responseTime;

    try {
      const startTime = Date.now();

      response = await axios({
        method: method || "GET",
        url: `${this.baseUrl}${endpoint}`,
        headers: headers || {},
        data: body,
        timeout: this.timeout,
        validateStatus: () => true, // 允许所有状态码
      });

      responseTime = Date.now() - startTime;
    } catch (error) {
      throw new Error(`API request failed: ${error.message}`);
    }

    // 创建当前快照
    const currentSnapshot = await this.snapshotManager.createApiSnapshot(
      name,
      response,
      {
        url: endpoint,
        method: method || "GET",
        responseTime,
      },
    );

    // 获取基线快照
    const baseline = await this.snapshotManager.getBaseline(name, "api");

    if (!baseline) {
      console.log(`No baseline found for ${name}, creating new baseline`);
      await this.snapshotManager.updateBaseline(name, currentSnapshot, "api");
      return {
        status: "baseline_created",
        message: `Baseline created for ${name}`,
        snapshot: currentSnapshot,
      };
    }

    // 执行回归检查
    const regressionResult = this.compareSnapshots(
      baseline,
      currentSnapshot,
      testCase,
    );

    return {
      status: regressionResult.passed ? "passed" : "failed",
      message: regressionResult.message,
      differences: regressionResult.differences,
      baseline,
      current: currentSnapshot,
    };
  }

  /**
   * 比较快照
   * @param {Object} baseline - 基线快照
   * @param {Object} current - 当前快照
   * @param {Object} testCase - 测试用例配置
   */
  compareSnapshots(baseline, current, testCase) {
    const differences = [];
    let passed = true;

    // 1. 检查状态码
    if (baseline.metadata.statusCode !== current.metadata.statusCode) {
      differences.push({
        type: "status_code",
        expected: baseline.metadata.statusCode,
        actual: current.metadata.statusCode,
        severity: "critical",
      });
      passed = false;
    }

    // 2. 检查响应结构
    const structureDiff = this.compareStructure(baseline.data, current.data);
    if (structureDiff.length > 0) {
      differences.push(
        ...structureDiff.map((diff) => ({
          ...diff,
          type: "structure",
          severity: "high",
        })),
      );
      passed = false;
    }

    // 3. 检查关键字段
    if (testCase.criticalFields) {
      const fieldDiff = this.compareCriticalFields(
        baseline.data,
        current.data,
        testCase.criticalFields,
      );
      if (fieldDiff.length > 0) {
        differences.push(
          ...fieldDiff.map((diff) => ({
            ...diff,
            type: "critical_field",
            severity: "high",
          })),
        );
        passed = false;
      }
    }

    // 4. 检查响应时间
    if (testCase.performanceThreshold) {
      const responseTime = current.metadata.responseTime;
      const threshold = testCase.performanceThreshold;

      if (responseTime > threshold) {
        differences.push({
          type: "performance",
          field: "responseTime",
          expected: `<= ${threshold}ms`,
          actual: `${responseTime}ms`,
          severity: "medium",
        });
        // 性能问题不一定导致测试失败，取决于配置
        if (testCase.strictPerformance) {
          passed = false;
        }
      }
    }

    // 5. 检查响应头
    if (testCase.checkHeaders) {
      const headerDiff = this.compareHeaders(
        baseline.metadata.headers,
        current.metadata.headers,
        testCase.criticalHeaders || [],
      );
      if (headerDiff.length > 0) {
        differences.push(
          ...headerDiff.map((diff) => ({
            ...diff,
            type: "header",
            severity: "low",
          })),
        );
        // 头部差异通常不导致测试失败，除非是关键头部
        if (testCase.strictHeaders) {
          passed = false;
        }
      }
    }

    return {
      passed,
      differences,
      message: passed
        ? `API regression test passed for ${testCase.name}`
        : `API regression detected for ${testCase.name}: ${differences.length} differences found`,
    };
  }

  /**
   * 比较数据结构
   * @param {any} baseline - 基线数据
   * @param {any} current - 当前数据
   * @param {string} path - 当前路径
   */
  compareStructure(baseline, current, path = "") {
    const differences = [];

    // 类型检查
    if (typeof baseline !== typeof current) {
      differences.push({
        path,
        expected: typeof baseline,
        actual: typeof current,
        message: `Type mismatch at ${path}`,
      });
      return differences;
    }

    // 数组检查
    if (Array.isArray(baseline)) {
      if (!Array.isArray(current)) {
        differences.push({
          path,
          expected: "array",
          actual: typeof current,
          message: `Expected array at ${path}`,
        });
        return differences;
      }

      // 检查数组长度（可选）
      if (baseline.length !== current.length) {
        differences.push({
          path: `${path}.length`,
          expected: baseline.length,
          actual: current.length,
          message: `Array length mismatch at ${path}`,
        });
      }

      // 检查数组元素结构（取第一个元素作为样本）
      if (baseline.length > 0 && current.length > 0) {
        const elementDiff = this.compareStructure(
          baseline[0],
          current[0],
          `${path}[0]`,
        );
        differences.push(...elementDiff);
      }

      return differences;
    }

    // 对象检查
    if (baseline && typeof baseline === "object") {
      if (!current || typeof current !== "object") {
        differences.push({
          path,
          expected: "object",
          actual: typeof current,
          message: `Expected object at ${path}`,
        });
        return differences;
      }

      // 检查缺失的键
      Object.keys(baseline).forEach((key) => {
        if (!(key in current)) {
          differences.push({
            path: `${path}.${key}`,
            expected: "present",
            actual: "missing",
            message: `Missing key ${key} at ${path}`,
          });
        } else {
          // 递归检查嵌套结构
          const nestedDiff = this.compareStructure(
            baseline[key],
            current[key],
            `${path}.${key}`,
          );
          differences.push(...nestedDiff);
        }
      });

      // 检查新增的键
      Object.keys(current).forEach((key) => {
        if (!(key in baseline)) {
          differences.push({
            path: `${path}.${key}`,
            expected: "absent",
            actual: "present",
            message: `Unexpected key ${key} at ${path}`,
          });
        }
      });
    }

    return differences;
  }

  /**
   * 比较关键字段
   * @param {Object} baseline - 基线数据
   * @param {Object} current - 当前数据
   * @param {Array} criticalFields - 关键字段列表
   */
  compareCriticalFields(baseline, current, criticalFields) {
    const differences = [];

    criticalFields.forEach((fieldPath) => {
      const baselineValue = this.getNestedValue(baseline, fieldPath);
      const currentValue = this.getNestedValue(current, fieldPath);

      if (JSON.stringify(baselineValue) !== JSON.stringify(currentValue)) {
        differences.push({
          field: fieldPath,
          expected: baselineValue,
          actual: currentValue,
          message: `Critical field ${fieldPath} value changed`,
        });
      }
    });

    return differences;
  }

  /**
   * 比较响应头
   * @param {Object} baselineHeaders - 基线响应头
   * @param {Object} currentHeaders - 当前响应头
   * @param {Array} criticalHeaders - 关键响应头
   */
  compareHeaders(baselineHeaders, currentHeaders, criticalHeaders) {
    const differences = [];

    criticalHeaders.forEach((header) => {
      const baselineValue = baselineHeaders[header];
      const currentValue = currentHeaders[header];

      if (baselineValue !== currentValue) {
        differences.push({
          header,
          expected: baselineValue,
          actual: currentValue,
          message: `Critical header ${header} value changed`,
        });
      }
    });

    return differences;
  }

  /**
   * 获取嵌套对象的值
   * @param {Object} obj - 对象
   * @param {string} path - 路径（如 'user.profile.name'）
   */
  getNestedValue(obj, path) {
    return path.split(".").reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  /**
   * 批量运行API回归测试
   * @param {Array} testCases - 测试用例数组
   */
  async runBatchTests(testCases) {
    const results = [];

    for (const testCase of testCases) {
      try {
        const result = await this.runApiTest(testCase);
        results.push({
          testCase: testCase.name,
          ...result,
        });
      } catch (error) {
        results.push({
          testCase: testCase.name,
          status: "error",
          message: error.message,
          error: error.stack,
        });
      }
    }

    return results;
  }
}

// Jest测试套件
describe("API Regression Tests", () => {
  let tester;

  beforeAll(() => {
    tester = new ApiRegressionTester();
  });

  // 从配置文件加载测试用例
  const testCases = config.api.endpoints || [];

  testCases.forEach((testCase) => {
    test(`API Regression: ${testCase.name}`, async () => {
      const result = await tester.runApiTest(testCase);

      if (result.status === "failed") {
        console.error("Regression detected:", result.differences);

        // 根据严重程度决定是否失败
        const criticalIssues = result.differences.filter(
          (diff) => diff.severity === "critical" || diff.severity === "high",
        );

        if (criticalIssues.length > 0) {
          throw new Error(result.message);
        } else {
          console.warn(
            "Non-critical differences detected:",
            result.differences,
          );
        }
      }

      expect(result.status).toMatch(/passed|baseline_created/);
    }, 30000); // 30秒超时
  });

  // 性能回归测试
  test("API Performance Regression", async () => {
    const performanceTests = testCases.filter((tc) => tc.performanceThreshold);

    if (performanceTests.length === 0) {
      console.log("No performance tests configured");
      return;
    }

    const results = await tester.runBatchTests(performanceTests);
    const slowTests = results.filter(
      (r) =>
        r.differences && r.differences.some((d) => d.type === "performance"),
    );

    if (slowTests.length > 0) {
      console.warn("Performance regression detected:", slowTests);

      // 如果配置了严格性能检查，则失败
      const strictTests = slowTests.filter(
        (t) =>
          performanceTests.find((pt) => pt.name === t.testCase)
            ?.strictPerformance,
      );

      if (strictTests.length > 0) {
        throw new Error(
          `Performance regression in: ${strictTests
            .map((t) => t.testCase)
            .join(", ")}`,
        );
      }
    }
  });
});

module.exports = ApiRegressionTester;
