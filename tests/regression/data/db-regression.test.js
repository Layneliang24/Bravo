/**
 * 数据库回归测试套件
 * 用于检测数据库结构和数据一致性的回归问题
 */

const { Pool } = require("pg");
const mysql = require("mysql2/promise");
const sqlite3 = require("sqlite3");
const { promisify } = require("util");
const SnapshotManager = require("../utils/snapshot");
const config = require("../config/regression.config");

class DbRegressionTester {
  constructor() {
    this.snapshotManager = new SnapshotManager(config.snapshot);
    this.dbConfig = config.database;
    this.connection = null;
  }

  /**
   * 连接数据库
   */
  async connect() {
    const { type, connection } = this.dbConfig;

    try {
      switch (type) {
        case "postgresql":
          this.connection = new Pool(connection);
          break;
        case "mysql":
          this.connection = await mysql.createConnection(connection);
          break;
        case "sqlite":
          this.connection = new sqlite3.Database(connection.database);
          this.connection.all = promisify(
            this.connection.all.bind(this.connection),
          );
          this.connection.run = promisify(
            this.connection.run.bind(this.connection),
          );
          break;
        default:
          throw new Error(`Unsupported database type: ${type}`);
      }

      console.log(`Connected to ${type} database`);
    } catch (error) {
      throw new Error(`Database connection failed: ${error.message}`);
    }
  }

  /**
   * 断开数据库连接
   */
  async disconnect() {
    if (this.connection) {
      const { type } = this.dbConfig;

      switch (type) {
        case "postgresql":
          await this.connection.end();
          break;
        case "mysql":
          await this.connection.end();
          break;
        case "sqlite":
          this.connection.close();
          break;
      }

      this.connection = null;
      console.log("Database connection closed");
    }
  }

  /**
   * 执行数据库回归测试
   * @param {Object} testCase - 测试用例
   */
  async runDbTest(testCase) {
    const { name, type, query, tables, checkConstraints, checkIndexes } =
      testCase;

    console.log(`Running DB regression test: ${name}`);

    if (!this.connection) {
      await this.connect();
    }

    try {
      let testData = {};

      switch (type) {
        case "schema":
          testData = await this.captureSchema(tables);
          break;
        case "data":
          testData = await this.captureData(query, tables);
          break;
        case "constraints":
          testData = await this.captureConstraints(tables);
          break;
        case "indexes":
          testData = await this.captureIndexes(tables);
          break;
        case "custom":
          testData = await this.executeCustomQuery(query);
          break;
        default:
          throw new Error(`Unknown test type: ${type}`);
      }

      // 创建当前快照
      const currentSnapshot = await this.snapshotManager.createDbSnapshot(
        name,
        testData,
        {
          testType: type,
          tables: tables || [],
          query: query || null,
        },
      );

      // 获取基线快照
      const baseline = await this.snapshotManager.getBaseline(name, "db");

      if (!baseline) {
        console.log(`No baseline found for ${name}, creating new baseline`);
        await this.snapshotManager.updateBaseline(name, currentSnapshot, "db");
        return {
          status: "baseline_created",
          message: `Baseline created for ${name}`,
          snapshot: currentSnapshot,
        };
      }

      // 执行回归检查
      const regressionResult = this.compareDbSnapshots(
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
    } catch (error) {
      throw new Error(`DB test failed: ${error.message}`);
    }
  }

  /**
   * 捕获数据库架构
   * @param {Array} tables - 表名列表
   */
  async captureSchema(tables = []) {
    const schema = {};
    const { type } = this.dbConfig;

    if (tables.length === 0) {
      // 获取所有表
      tables = await this.getAllTables();
    }

    for (const table of tables) {
      schema[table] = await this.getTableSchema(table);
    }

    return schema;
  }

  /**
   * 捕获数据
   * @param {string} query - 查询语句
   * @param {Array} tables - 表名列表
   */
  async captureData(query, tables = []) {
    const data = {};

    if (query) {
      // 执行自定义查询
      data.custom_query = await this.executeQuery(query);
    } else if (tables.length > 0) {
      // 捕获指定表的数据
      for (const table of tables) {
        data[table] = await this.executeQuery(
          `SELECT * FROM ${table} ORDER BY id`,
        );
      }
    } else {
      throw new Error(
        "Either query or tables must be specified for data capture",
      );
    }

    return data;
  }

  /**
   * 捕获约束信息
   * @param {Array} tables - 表名列表
   */
  async captureConstraints(tables = []) {
    const constraints = {};
    const { type } = this.dbConfig;

    if (tables.length === 0) {
      tables = await this.getAllTables();
    }

    for (const table of tables) {
      constraints[table] = await this.getTableConstraints(table);
    }

    return constraints;
  }

  /**
   * 捕获索引信息
   * @param {Array} tables - 表名列表
   */
  async captureIndexes(tables = []) {
    const indexes = {};
    const { type } = this.dbConfig;

    if (tables.length === 0) {
      tables = await this.getAllTables();
    }

    for (const table of tables) {
      indexes[table] = await this.getTableIndexes(table);
    }

    return indexes;
  }

  /**
   * 执行自定义查询
   * @param {string} query - 查询语句
   */
  async executeCustomQuery(query) {
    return await this.executeQuery(query);
  }

  /**
   * 执行查询
   * @param {string} query - 查询语句
   */
  async executeQuery(query) {
    const { type } = this.dbConfig;

    try {
      switch (type) {
        case "postgresql":
          const pgResult = await this.connection.query(query);
          return pgResult.rows;
        case "mysql":
          const [mysqlRows] = await this.connection.execute(query);
          return mysqlRows;
        case "sqlite":
          return await this.connection.all(query);
        default:
          throw new Error(`Unsupported database type: ${type}`);
      }
    } catch (error) {
      throw new Error(`Query execution failed: ${error.message}`);
    }
  }

  /**
   * 获取所有表名
   */
  async getAllTables() {
    const { type } = this.dbConfig;
    let query;

    switch (type) {
      case "postgresql":
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'";
        break;
      case "mysql":
        query = "SHOW TABLES";
        break;
      case "sqlite":
        query = "SELECT name FROM sqlite_master WHERE type='table'";
        break;
      default:
        throw new Error(`Unsupported database type: ${type}`);
    }

    const result = await this.executeQuery(query);

    switch (type) {
      case "postgresql":
        return result.map((row) => row.tablename);
      case "mysql":
        return result.map((row) => Object.values(row)[0]);
      case "sqlite":
        return result.map((row) => row.name);
    }
  }

  /**
   * 获取表结构
   * @param {string} tableName - 表名
   */
  async getTableSchema(tableName) {
    const { type } = this.dbConfig;
    let query;

    switch (type) {
      case "postgresql":
        query = `
          SELECT column_name, data_type, is_nullable, column_default
          FROM information_schema.columns
          WHERE table_name = '${tableName}'
          ORDER BY ordinal_position
        `;
        break;
      case "mysql":
        query = `DESCRIBE ${tableName}`;
        break;
      case "sqlite":
        query = `PRAGMA table_info(${tableName})`;
        break;
      default:
        throw new Error(`Unsupported database type: ${type}`);
    }

    return await this.executeQuery(query);
  }

  /**
   * 获取表约束
   * @param {string} tableName - 表名
   */
  async getTableConstraints(tableName) {
    const { type } = this.dbConfig;
    let query;

    switch (type) {
      case "postgresql":
        query = `
          SELECT constraint_name, constraint_type
          FROM information_schema.table_constraints
          WHERE table_name = '${tableName}'
        `;
        break;
      case "mysql":
        query = `
          SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
          FROM information_schema.TABLE_CONSTRAINTS
          WHERE TABLE_NAME = '${tableName}'
        `;
        break;
      case "sqlite":
        // SQLite约束信息较难获取，使用表信息
        query = `PRAGMA table_info(${tableName})`;
        break;
      default:
        throw new Error(`Unsupported database type: ${type}`);
    }

    return await this.executeQuery(query);
  }

  /**
   * 获取表索引
   * @param {string} tableName - 表名
   */
  async getTableIndexes(tableName) {
    const { type } = this.dbConfig;
    let query;

    switch (type) {
      case "postgresql":
        query = `
          SELECT indexname, indexdef
          FROM pg_indexes
          WHERE tablename = '${tableName}'
        `;
        break;
      case "mysql":
        query = `SHOW INDEX FROM ${tableName}`;
        break;
      case "sqlite":
        query = `PRAGMA index_list(${tableName})`;
        break;
      default:
        throw new Error(`Unsupported database type: ${type}`);
    }

    return await this.executeQuery(query);
  }

  /**
   * 比较数据库快照
   * @param {Object} baseline - 基线快照
   * @param {Object} current - 当前快照
   * @param {Object} testCase - 测试用例
   */
  compareDbSnapshots(baseline, current, testCase) {
    const differences = [];
    let passed = true;

    // 比较数据结构
    const structureDiff = this.compareObjectStructure(
      baseline.data,
      current.data,
      "root",
    );

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

    // 比较数据内容（如果是数据测试）
    if (testCase.type === "data") {
      const dataDiff = this.compareDataContent(
        baseline.data,
        current.data,
        testCase.ignoreFields || [],
      );

      if (dataDiff.length > 0) {
        differences.push(
          ...dataDiff.map((diff) => ({
            ...diff,
            type: "data",
            severity: testCase.strictData ? "high" : "medium",
          })),
        );

        if (testCase.strictData) {
          passed = false;
        }
      }
    }

    // 比较记录数量
    const baselineCount = baseline.metadata.recordCount || 0;
    const currentCount = current.metadata.recordCount || 0;

    if (baselineCount !== currentCount) {
      differences.push({
        type: "record_count",
        field: "total_records",
        expected: baselineCount,
        actual: currentCount,
        severity: "medium",
      });

      if (testCase.strictCount) {
        passed = false;
      }
    }

    return {
      passed,
      differences,
      message: passed
        ? `DB regression test passed for ${testCase.name}`
        : `DB regression detected for ${testCase.name}: ${differences.length} differences found`,
    };
  }

  /**
   * 比较对象结构
   * @param {Object} baseline - 基线对象
   * @param {Object} current - 当前对象
   * @param {string} path - 当前路径
   */
  compareObjectStructure(baseline, current, path = "") {
    const differences = [];

    // 检查缺失的键
    Object.keys(baseline).forEach((key) => {
      if (!(key in current)) {
        differences.push({
          path: `${path}.${key}`,
          expected: "present",
          actual: "missing",
          message: `Missing key ${key} at ${path}`,
        });
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

    return differences;
  }

  /**
   * 比较数据内容
   * @param {Object} baseline - 基线数据
   * @param {Object} current - 当前数据
   * @param {Array} ignoreFields - 忽略的字段
   */
  compareDataContent(baseline, current, ignoreFields = []) {
    const differences = [];

    Object.keys(baseline).forEach((table) => {
      if (current[table]) {
        const baselineData = baseline[table];
        const currentData = current[table];

        if (Array.isArray(baselineData) && Array.isArray(currentData)) {
          // 比较记录数量
          if (baselineData.length !== currentData.length) {
            differences.push({
              table,
              field: "record_count",
              expected: baselineData.length,
              actual: currentData.length,
              message: `Record count mismatch in table ${table}`,
            });
          }

          // 比较记录内容（取样本）
          const sampleSize = Math.min(
            baselineData.length,
            currentData.length,
            10,
          );
          for (let i = 0; i < sampleSize; i++) {
            const baselineRecord = baselineData[i];
            const currentRecord = currentData[i];

            if (baselineRecord && currentRecord) {
              const recordDiff = this.compareRecords(
                baselineRecord,
                currentRecord,
                ignoreFields,
                `${table}[${i}]`,
              );
              differences.push(...recordDiff);
            }
          }
        }
      }
    });

    return differences;
  }

  /**
   * 比较记录
   * @param {Object} baseline - 基线记录
   * @param {Object} current - 当前记录
   * @param {Array} ignoreFields - 忽略的字段
   * @param {string} path - 路径
   */
  compareRecords(baseline, current, ignoreFields, path) {
    const differences = [];

    Object.keys(baseline).forEach((field) => {
      if (!ignoreFields.includes(field)) {
        if (baseline[field] !== current[field]) {
          differences.push({
            path: `${path}.${field}`,
            field,
            expected: baseline[field],
            actual: current[field],
            message: `Field ${field} value changed at ${path}`,
          });
        }
      }
    });

    return differences;
  }

  /**
   * 批量运行数据库回归测试
   * @param {Array} testCases - 测试用例数组
   */
  async runBatchTests(testCases) {
    const results = [];

    await this.connect();

    try {
      for (const testCase of testCases) {
        try {
          const result = await this.runDbTest(testCase);
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
    } finally {
      await this.disconnect();
    }

    return results;
  }
}

// Jest测试套件
describe("Database Regression Tests", () => {
  let tester;

  beforeAll(async () => {
    tester = new DbRegressionTester();
  });

  afterAll(async () => {
    await tester.disconnect();
  });

  // 从配置文件加载测试用例
  const testCases = config.database.tests || [];

  testCases.forEach((testCase) => {
    test(`DB Regression: ${testCase.name}`, async () => {
      const result = await tester.runDbTest(testCase);

      if (result.status === "failed") {
        console.error("DB regression detected:", result.differences);

        // 根据严重程度决定是否失败
        const criticalIssues = result.differences.filter(
          (diff) => diff.severity === "high",
        );

        if (criticalIssues.length > 0) {
          throw new Error(result.message);
        } else {
          console.warn(
            "Non-critical DB differences detected:",
            result.differences,
          );
        }
      }

      expect(result.status).toMatch(/passed|baseline_created/);
    }, 60000); // 60秒超时
  });

  // 数据一致性测试
  test("Database Consistency Check", async () => {
    const consistencyTests = testCases.filter(
      (tc) => tc.type === "data" && tc.strictData,
    );

    if (consistencyTests.length === 0) {
      console.log("No consistency tests configured");
      return;
    }

    const results = await tester.runBatchTests(consistencyTests);
    const failedTests = results.filter((r) => r.status === "failed");

    if (failedTests.length > 0) {
      throw new Error(
        `Data consistency issues in: ${failedTests
          .map((t) => t.testCase)
          .join(", ")}`,
      );
    }
  });
});

module.exports = DbRegressionTester;
