/**
 * 快照工具 - 用于创建和管理测试快照
 */

const fs = require("fs").promises;
const path = require("path");
const crypto = require("crypto");
const { execSync } = require("child_process");

class SnapshotManager {
  constructor(config = {}) {
    this.config = {
      snapshotDir: config.snapshotDir || "./tests/regression/data/snapshots",
      baselineDir: config.baselineDir || "./tests/regression/config/baselines",
      format: config.format || "json",
      compression: config.compression || false,
      ...config,
    };

    this.ensureDirectories();
  }

  /**
   * 确保快照目录存在
   */
  async ensureDirectories() {
    const dirs = [this.config.snapshotDir, this.config.baselineDir];

    for (const dir of dirs) {
      try {
        await fs.access(dir);
      } catch {
        await fs.mkdir(dir, { recursive: true });
      }
    }
  }

  /**
   * 创建API响应快照
   * @param {string} testName - 测试名称
   * @param {Object} response - API响应数据
   * @param {Object} metadata - 元数据
   */
  async createApiSnapshot(testName, response, metadata = {}) {
    const snapshot = {
      testName,
      timestamp: new Date().toISOString(),
      metadata: {
        url: metadata.url,
        method: metadata.method,
        statusCode: response.status,
        headers: this.sanitizeHeaders(response.headers),
        responseTime: metadata.responseTime,
        ...metadata,
      },
      data: this.sanitizeResponseData(response.data),
      hash: this.generateHash(response.data),
    };

    const filename = this.generateFilename(testName, "api");
    const filepath = path.join(this.config.snapshotDir, filename);

    await this.writeSnapshot(filepath, snapshot);
    return snapshot;
  }

  /**
   * 创建UI快照
   * @param {string} testName - 测试名称
   * @param {Buffer} screenshot - 截图数据
   * @param {Object} metadata - 元数据
   */
  async createUiSnapshot(testName, screenshot, metadata = {}) {
    const snapshot = {
      testName,
      timestamp: new Date().toISOString(),
      metadata: {
        viewport: metadata.viewport,
        browser: metadata.browser,
        url: metadata.url,
        ...metadata,
      },
      hash: this.generateHash(screenshot),
    };

    // 保存截图文件
    const imageFilename = this.generateFilename(testName, "ui", "png");
    const imagePath = path.join(this.config.snapshotDir, imageFilename);
    await fs.writeFile(imagePath, screenshot);

    // 保存元数据
    const metaFilename = this.generateFilename(testName, "ui", "json");
    const metaPath = path.join(this.config.snapshotDir, metaFilename);
    await this.writeSnapshot(metaPath, snapshot);

    return { ...snapshot, imagePath, metaPath };
  }

  /**
   * 创建数据库快照
   * @param {string} testName - 测试名称
   * @param {Object} dbData - 数据库数据
   * @param {Object} metadata - 元数据
   */
  async createDbSnapshot(testName, dbData, metadata = {}) {
    const snapshot = {
      testName,
      timestamp: new Date().toISOString(),
      metadata: {
        tables: Object.keys(dbData),
        recordCount: this.countRecords(dbData),
        ...metadata,
      },
      data: this.sanitizeDbData(dbData),
      hash: this.generateHash(dbData),
    };

    const filename = this.generateFilename(testName, "db");
    const filepath = path.join(this.config.snapshotDir, filename);

    await this.writeSnapshot(filepath, snapshot);
    return snapshot;
  }

  /**
   * 获取基线快照
   * @param {string} testName - 测试名称
   * @param {string} type - 快照类型
   */
  async getBaseline(testName, type) {
    const filename = this.generateFilename(testName, type);
    const filepath = path.join(this.config.baselineDir, filename);

    try {
      const content = await fs.readFile(filepath, "utf8");
      return JSON.parse(content);
    } catch (error) {
      if (error.code === "ENOENT") {
        return null; // 基线不存在
      }
      throw error;
    }
  }

  /**
   * 更新基线快照
   * @param {string} testName - 测试名称
   * @param {Object} snapshot - 快照数据
   * @param {string} type - 快照类型
   */
  async updateBaseline(testName, snapshot, type) {
    const filename = this.generateFilename(testName, type);
    const filepath = path.join(this.config.baselineDir, filename);

    await this.writeSnapshot(filepath, snapshot);

    // 如果是UI快照，还需要复制图片文件
    if (type === "ui" && snapshot.imagePath) {
      const baselineImagePath = path.join(
        this.config.baselineDir,
        path.basename(snapshot.imagePath),
      );
      await fs.copyFile(snapshot.imagePath, baselineImagePath);
    }
  }

  /**
   * 清理过期快照
   * @param {number} maxAge - 最大保留天数
   */
  async cleanupSnapshots(maxAge = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - maxAge);

    const files = await fs.readdir(this.config.snapshotDir);

    for (const file of files) {
      const filepath = path.join(this.config.snapshotDir, file);
      const stats = await fs.stat(filepath);

      if (stats.mtime < cutoffDate) {
        await fs.unlink(filepath);
        console.log(`Cleaned up old snapshot: ${file}`);
      }
    }
  }

  /**
   * 生成文件名
   * @param {string} testName - 测试名称
   * @param {string} type - 类型
   * @param {string} extension - 文件扩展名
   */
  generateFilename(testName, type, extension = "json") {
    const sanitized = testName.replace(/[^a-zA-Z0-9-_]/g, "_");
    const timestamp = new Date().toISOString().split("T")[0];
    return `${sanitized}_${type}_${timestamp}.${extension}`;
  }

  /**
   * 生成数据哈希
   * @param {any} data - 数据
   */
  generateHash(data) {
    const content = typeof data === "string" ? data : JSON.stringify(data);
    return crypto.createHash("sha256").update(content).digest("hex");
  }

  /**
   * 写入快照文件
   * @param {string} filepath - 文件路径
   * @param {Object} data - 数据
   */
  async writeSnapshot(filepath, data) {
    const content = JSON.stringify(data, null, 2);

    if (this.config.compression) {
      const zlib = require("zlib");
      const compressed = zlib.gzipSync(content);
      await fs.writeFile(filepath + ".gz", compressed);
    } else {
      await fs.writeFile(filepath, content, "utf8");
    }
  }

  /**
   * 清理响应头（移除敏感信息）
   * @param {Object} headers - 响应头
   */
  sanitizeHeaders(headers) {
    const sanitized = { ...headers };
    const sensitiveHeaders = [
      "authorization",
      "cookie",
      "set-cookie",
      "x-api-key",
      "x-auth-token",
    ];

    sensitiveHeaders.forEach((header) => {
      if (sanitized[header]) {
        sanitized[header] = "[REDACTED]";
      }
    });

    return sanitized;
  }

  /**
   * 清理响应数据（移除动态字段）
   * @param {any} data - 响应数据
   */
  sanitizeResponseData(data) {
    if (!data || typeof data !== "object") {
      return data;
    }

    const sanitized = JSON.parse(JSON.stringify(data));
    const dynamicFields = [
      "timestamp",
      "created_at",
      "updated_at",
      "request_id",
      "trace_id",
      "session_id",
    ];

    this.removeDynamicFields(sanitized, dynamicFields);
    return sanitized;
  }

  /**
   * 清理数据库数据
   * @param {Object} dbData - 数据库数据
   */
  sanitizeDbData(dbData) {
    const sanitized = JSON.parse(JSON.stringify(dbData));
    const dynamicFields = [
      "created_at",
      "updated_at",
      "last_login",
      "password",
      "token",
      "secret",
    ];

    Object.keys(sanitized).forEach((table) => {
      if (Array.isArray(sanitized[table])) {
        sanitized[table].forEach((record) => {
          this.removeDynamicFields(record, dynamicFields);
        });
      }
    });

    return sanitized;
  }

  /**
   * 递归移除动态字段
   * @param {Object} obj - 对象
   * @param {Array} fields - 要移除的字段
   */
  removeDynamicFields(obj, fields) {
    if (!obj || typeof obj !== "object") {
      return;
    }

    fields.forEach((field) => {
      if (obj.hasOwnProperty(field)) {
        delete obj[field];
      }
    });

    Object.values(obj).forEach((value) => {
      if (typeof value === "object") {
        this.removeDynamicFields(value, fields);
      }
    });
  }

  /**
   * 统计记录数量
   * @param {Object} dbData - 数据库数据
   */
  countRecords(dbData) {
    let total = 0;
    Object.values(dbData).forEach((table) => {
      if (Array.isArray(table)) {
        total += table.length;
      }
    });
    return total;
  }
}

module.exports = SnapshotManager;
