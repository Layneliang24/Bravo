// Selenium WebDriver 配置文件
// 用于自动化浏览器测试

const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const firefox = require('selenium-webdriver/firefox');
const edge = require('selenium-webdriver/edge');

// 浏览器配置
const BROWSERS = {
  chrome: {
    name: 'chrome',
    options: new chrome.Options()
      .addArguments('--headless')
      .addArguments('--no-sandbox')
      .addArguments('--disable-dev-shm-usage')
      .addArguments('--disable-gpu')
      .addArguments('--window-size=1920,1080')
      .addArguments('--disable-extensions')
      .addArguments('--disable-web-security')
      .addArguments('--allow-running-insecure-content'),
  },

  firefox: {
    name: 'firefox',
    options: new firefox.Options()
      .addArguments('--headless')
      .addArguments('--width=1920')
      .addArguments('--height=1080'),
  },

  edge: {
    name: 'MicrosoftEdge',
    options: new edge.Options()
      .addArguments('--headless')
      .addArguments('--no-sandbox')
      .addArguments('--disable-dev-shm-usage')
      .addArguments('--window-size=1920,1080'),
  },
};

// 测试环境配置
const TEST_CONFIG = {
  // 基础URL
  baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3001',

  // 超时设置
  timeouts: {
    implicit: 10000, // 隐式等待
    pageLoad: 30000, // 页面加载超时
    script: 30000, // 脚本执行超时
  },

  // 重试配置
  retry: {
    attempts: 3,
    delay: 1000,
  },

  // 截图配置
  screenshot: {
    onFailure: true,
    directory: './tests/reports/screenshots',
  },
};

// WebDriver 工厂类
class WebDriverFactory {
  /**
   * 创建 WebDriver 实例
   * @param {string} browserName - 浏览器名称 (chrome, firefox, edge)
   * @param {Object} customOptions - 自定义选项
   * @returns {WebDriver} WebDriver 实例
   */
  static async createDriver(browserName = 'chrome', customOptions = {}) {
    const browser = BROWSERS[browserName.toLowerCase()];
    if (!browser) {
      throw new Error(`不支持的浏览器: ${browserName}`);
    }

    let builder = new Builder().forBrowser(browser.name);

    // 应用浏览器选项
    switch (browserName.toLowerCase()) {
      case 'chrome':
        builder = builder.setChromeOptions(browser.options);
        break;
      case 'firefox':
        builder = builder.setFirefoxOptions(browser.options);
        break;
      case 'edge':
        builder = builder.setEdgeOptions(browser.options);
        break;
    }

    const driver = await builder.build();

    // 设置超时
    await driver.manage().setTimeouts(TEST_CONFIG.timeouts);

    return driver;
  }

  /**
   * 创建多个浏览器实例进行并行测试
   * @param {Array} browsers - 浏览器列表
   * @returns {Array} WebDriver 实例数组
   */
  static async createMultipleDrivers(browsers = ['chrome']) {
    const drivers = [];
    for (const browser of browsers) {
      try {
        const driver = await this.createDriver(browser);
        drivers.push({ browser, driver });
      } catch (error) {
        console.warn(`无法创建 ${browser} 驱动: ${error.message}`);
      }
    }
    return drivers;
  }
}

// 测试辅助工具类
class TestHelper {
  constructor(driver) {
    this.driver = driver;
  }

  /**
   * 导航到指定页面
   * @param {string} path - 页面路径
   */
  async navigateTo(path = '') {
    const url = `${TEST_CONFIG.baseUrl}${path}`;
    await this.driver.get(url);
    await this.waitForPageLoad();
  }

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad() {
    await this.driver.wait(until.elementLocated(By.tagName('body')), TEST_CONFIG.timeouts.pageLoad);
  }

  /**
   * 查找元素
   * @param {By} locator - 元素定位器
   * @param {number} timeout - 超时时间
   */
  async findElement(locator, timeout = TEST_CONFIG.timeouts.implicit) {
    return await this.driver.wait(until.elementLocated(locator), timeout);
  }

  /**
   * 查找多个元素
   * @param {By} locator - 元素定位器
   */
  async findElements(locator) {
    return await this.driver.findElements(locator);
  }

  /**
   * 点击元素
   * @param {By} locator - 元素定位器
   */
  async clickElement(locator) {
    const element = await this.findElement(locator);
    await this.driver.wait(until.elementIsEnabled(element));
    await element.click();
  }

  /**
   * 输入文本
   * @param {By} locator - 元素定位器
   * @param {string} text - 输入文本
   */
  async inputText(locator, text) {
    const element = await this.findElement(locator);
    await element.clear();
    await element.sendKeys(text);
  }

  /**
   * 获取元素文本
   * @param {By} locator - 元素定位器
   */
  async getElementText(locator) {
    const element = await this.findElement(locator);
    return await element.getText();
  }

  /**
   * 截图
   * @param {string} filename - 文件名
   */
  async takeScreenshot(filename) {
    const fs = require('fs');
    const path = require('path');

    const screenshot = await this.driver.takeScreenshot();
    const dir = TEST_CONFIG.screenshot.directory;

    // 确保目录存在
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const filepath = path.join(dir, `${filename}.png`);
    fs.writeFileSync(filepath, screenshot, 'base64');

    return filepath;
  }

  /**
   * 等待元素可见
   * @param {By} locator - 元素定位器
   * @param {number} timeout - 超时时间
   */
  async waitForElementVisible(locator, timeout = TEST_CONFIG.timeouts.implicit) {
    const element = await this.findElement(locator, timeout);
    await this.driver.wait(until.elementIsVisible(element), timeout);
    return element;
  }

  /**
   * 等待元素包含文本
   * @param {By} locator - 元素定位器
   * @param {string} text - 期望文本
   * @param {number} timeout - 超时时间
   */
  async waitForElementText(locator, text, timeout = TEST_CONFIG.timeouts.implicit) {
    await this.driver.wait(
      until.elementTextContains(await this.findElement(locator), text),
      timeout
    );
  }
}

module.exports = {
  WebDriverFactory,
  TestHelper,
  TEST_CONFIG,
  BROWSERS,
  By,
  until,
};
