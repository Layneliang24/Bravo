import { chromium, FullConfig } from '@playwright/test';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Playwright 全局设置
 * 在所有测试运行前执行的初始化操作
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 开始全局设置...');
  
  try {
    // 1. 清理之前的测试结果
    await cleanupPreviousResults();
    
    // 2. 检查测试环境
    await checkTestEnvironment();
    
    // 3. 准备测试数据
    await prepareTestData();
    
    // 4. 等待服务启动
    await waitForServices();
    
    // 5. 创建认证状态（如果需要）
    await setupAuthentication(config);
    
    console.log('✅ 全局设置完成');
  } catch (error) {
    console.error('❌ 全局设置失败:', error);
    throw error;
  }
}

/**
 * 清理之前的测试结果
 */
async function cleanupPreviousResults() {
  console.log('🧹 清理之前的测试结果...');
  
  const dirsToClean = [
    'test-results',
    'playwright-report',
    'coverage',
    'screenshots',
  ];
  
  for (const dir of dirsToClean) {
    const dirPath = path.join(__dirname, dir);
    if (fs.existsSync(dirPath)) {
      fs.rmSync(dirPath, { recursive: true, force: true });
      console.log(`  ✓ 已清理 ${dir}`);
    }
  }
}

/**
 * 检查测试环境
 */
async function checkTestEnvironment() {
  console.log('🔍 检查测试环境...');
  
  // 检查Node.js版本
  const nodeVersion = process.version;
  console.log(`  Node.js版本: ${nodeVersion}`);
  
  // 检查环境变量
  const requiredEnvVars = ['NODE_ENV'];
  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);
  
  if (missingEnvVars.length > 0) {
    console.warn(`  ⚠️  缺少环境变量: ${missingEnvVars.join(', ')}`);
  }
  
  // 设置默认环境变量
  if (!process.env.NODE_ENV) {
    process.env.NODE_ENV = 'test';
    console.log('  ✓ 设置 NODE_ENV=test');
  }
  
  if (!process.env.TEST_BASE_URL) {
    process.env.TEST_BASE_URL = 'http://localhost:3000';
    console.log('  ✓ 设置 TEST_BASE_URL=http://localhost:3000');
  }
}

/**
 * 准备测试数据
 */
async function prepareTestData() {
  console.log('📊 准备测试数据...');
  
  // 创建测试数据目录
  const testDataDir = path.join(__dirname, 'test-data');
  if (!fs.existsSync(testDataDir)) {
    fs.mkdirSync(testDataDir, { recursive: true });
    console.log('  ✓ 创建测试数据目录');
  }
  
  // 生成测试用户数据
  const testUsers = [
    {
      id: 1,
      username: 'testuser1',
      email: 'test1@example.com',
      password: 'password123',
      role: 'user'
    },
    {
      id: 2,
      username: 'admin',
      email: 'admin@example.com',
      password: 'admin123',
      role: 'admin'
    }
  ];
  
  const usersFile = path.join(testDataDir, 'users.json');
  fs.writeFileSync(usersFile, JSON.stringify(testUsers, null, 2));
  console.log('  ✓ 生成测试用户数据');
  
  // 生成测试博客数据
  const testBlogs = Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    title: `测试博客标题 ${i + 1}`,
    content: `这是测试博客 ${i + 1} 的内容。包含一些测试文本用于验证功能。`,
    author: i % 2 === 0 ? 'testuser1' : 'admin',
    category: ['技术', '生活', '随笔'][i % 3],
    tags: [`标签${i + 1}`, `tag${i + 1}`],
    createdAt: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
    published: true
  }));
  
  const blogsFile = path.join(testDataDir, 'blogs.json');
  fs.writeFileSync(blogsFile, JSON.stringify(testBlogs, null, 2));
  console.log('  ✓ 生成测试博客数据');
}

/**
 * 等待服务启动
 */
async function waitForServices() {
  console.log('⏳ 等待服务启动...');
  
  const services = [
    { name: '前端服务', url: 'http://localhost:3000', timeout: 60000 },
    { name: '后端API', url: 'http://localhost:8000/health', timeout: 60000 }
  ];
  
  for (const service of services) {
    await waitForService(service.name, service.url, service.timeout);
  }
}

/**
 * 等待单个服务启动
 */
async function waitForService(name: string, url: string, timeout: number) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const response = await fetch(url);
      if (response.ok || response.status < 500) {
        console.log(`  ✓ ${name} 已启动 (${url})`);
        return;
      }
    } catch (error) {
      // 服务还未启动，继续等待
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`${name} 启动超时 (${url})`);
}

/**
 * 设置认证状态
 */
async function setupAuthentication(config: FullConfig) {
  console.log('🔐 设置认证状态...');
  
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // 访问登录页面
    await page.goto(`${process.env.TEST_BASE_URL}/login`);
    
    // 模拟登录（如果登录页面存在）
    const loginForm = page.locator('form[data-testid="login-form"]');
    if (await loginForm.isVisible()) {
      await page.fill('[data-testid="username"]', 'testuser1');
      await page.fill('[data-testid="password"]', 'password123');
      await page.click('[data-testid="login-button"]');
      
      // 等待登录完成
      await page.waitForURL('**/dashboard', { timeout: 10000 });
      
      // 保存认证状态
      const storageState = await context.storageState();
      const authFile = path.join(__dirname, 'auth.json');
      fs.writeFileSync(authFile, JSON.stringify(storageState, null, 2));
      
      console.log('  ✓ 已保存认证状态');
    } else {
      console.log('  ℹ️  未找到登录表单，跳过认证设置');
    }
  } catch (error) {
    console.log('  ⚠️  认证设置失败，将使用匿名访问:', (error as Error).message);
  } finally {
    await browser.close();
  }
}

/**
 * 创建测试报告目录
 */
function createReportDirectories() {
  const dirs = [
    'playwright-report',
    'test-results',
    'coverage',
    'screenshots'
  ];
  
  dirs.forEach(dir => {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  });
}

// 创建报告目录
createReportDirectories();

export default globalSetup;

// 导出辅助函数供测试使用
export {
  cleanupPreviousResults,
  checkTestEnvironment,
  prepareTestData,
  waitForServices,
  setupAuthentication
};

// 类型定义
export interface TestUser {
  id: number;
  username: string;
  email: string;
  password: string;
  role: string;
}

export interface TestBlog {
  id: number;
  title: string;
  content: string;
  author: string;
  category: string;
  tags: string[];
  createdAt: string;
  published: boolean;
}