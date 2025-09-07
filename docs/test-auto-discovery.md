# 测试用例自动收录机制

## 概述

本项目已实现业内标准的测试用例自动收录机制，新增测试用例无需手动配置即可被自动发现和执行。

## 自动收录规则

### 1. 后端测试 (pytest)

**配置文件**: `backend/pytest.ini`

```ini
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
testpaths = apps tests
```

**自动收录规则**:
- 文件名: `test_*.py`, `*_tests.py`, `tests.py`
- 类名: `Test*`
- 函数名: `test_*`
- 目录: `apps/`, `tests/`

**示例**:
```python
# backend/tests/test_user.py
class TestUser:
    def test_create_user(self):
        pass
    
    def test_update_user(self):
        pass
```

### 2. 前端测试 (Vitest/Jest)

**配置文件**: `frontend/vitest.config.ts`

**自动收录规则**:
- 文件名: `*.test.js`, `*.test.ts`, `*.spec.js`, `*.spec.ts`
- 目录: `src/`, `tests/`

**示例**:
```javascript
// frontend/src/components/Button.test.js
describe('Button Component', () => {
  test('should render correctly', () => {
    // 测试代码
  });
});
```

### 3. E2E测试 (Playwright)

**配置文件**: `e2e/playwright.config.ts`

```typescript
export default defineConfig({
  testDir: './tests',
  testMatch: [
    '**/*.spec.ts',
    '**/*.spec.js',
    '**/*.test.ts',
    '**/*.test.js'
  ]
});
```

**自动收录规则**:
- 文件名: `*.spec.ts`, `*.spec.js`, `*.test.ts`, `*.test.js`
- 目录: `e2e/tests/`

**示例**:
```typescript
// e2e/tests/login.spec.ts
import { test, expect } from '@playwright/test';

test('用户登录', async ({ page }) => {
  // E2E测试代码
});
```

## 统一测试入口

### 1. 脚本入口

```bash
# 一键运行所有测试
bash test_all.sh

# 或使用npm
npm run test:all
```

### 2. Makefile入口

```bash
# 如果系统支持make
make test-all
```

### 3. 分层测试

```bash
# 单独运行各类测试
npm run test:frontend    # 前端测试
npm run test:backend     # 后端测试
npm run test:e2e         # E2E测试
```

## 新增测试用例步骤

### 后端测试

1. 在 `backend/tests/` 或 `backend/apps/*/tests/` 目录下创建文件
2. 文件名遵循 `test_*.py` 格式
3. 测试函数名以 `test_` 开头
4. 运行 `bash test_all.sh` 自动包含新测试

### 前端测试

1. 在组件同目录或 `frontend/tests/` 目录下创建文件
2. 文件名遵循 `*.test.js` 或 `*.spec.js` 格式
3. 使用标准测试框架语法
4. 运行 `bash test_all.sh` 自动包含新测试

### E2E测试

1. 在 `e2e/tests/` 目录下创建文件
2. 文件名遵循 `*.spec.ts` 格式
3. 使用Playwright测试语法
4. 运行 `bash test_all.sh` 自动包含新测试

## 验证自动收录

```bash
# 创建新测试文件后，运行以下命令验证
bash test_all.sh

# 查看测试发现情况
cd backend && pytest --collect-only
cd frontend && npm test -- --listTests
cd e2e && npx playwright test --list
```

## 最佳实践

1. **命名规范**: 严格遵循各框架的文件和函数命名规范
2. **目录结构**: 将测试文件放在约定的目录中
3. **测试分类**: 使用标记区分单元测试、集成测试、E2E测试
4. **持续验证**: 每次添加新测试后运行完整测试套件

## 故障排除

### 测试未被发现

1. 检查文件名是否符合命名规范
2. 检查文件位置是否在配置的测试目录中
3. 检查测试函数名是否以正确前缀开头
4. 运行 `--collect-only` 查看测试发现情况

### 测试执行失败

1. 检查依赖是否安装完整
2. 检查测试环境配置
3. 查看详细错误日志
4. 确认测试数据和Mock配置

---

✅ **总结**: 本项目已完全实现业内标准的测试自动收录机制，新增测试用例零配置即可被统一测试脚本发现和执行。