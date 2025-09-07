# 目录守卫指南

## 📁 文件放置规则

### ✅ 允许放置的位置

#### 文档类文件

- **产品文档** → `docs/00_product/`
- **使用指南** → `docs/01_guideline/`
- **测试报告** → `docs/02_test_report/`
- **操作文档** → `docs/03_operate/`

#### 测试文件

- **后端测试** → `backend/apps/<业务模块>/tests/`
  - 单元测试: `test_*.py`
  - 集成测试: `*_test.py`
- **前端测试** → `frontend/src/**/*.spec.ts`
- **E2E测试** → `e2e/tests/`

#### 配置文件

- **环境配置** → `.envs/`
- **CI配置** → `.github/workflows/`
- **脚本** → `scripts/`

### ❌ 禁止放置的位置

**根目录禁止放置以下类型文件：**

- `*.md` (除README.md, LICENSE)
- `*.txt`
- `test_*.py`
- `*_test.py`
- `*.keep`
- `*.example`

### 🚨 违规后果

1. **本地提交** → pre-commit钩子拦截
2. **远程推送** → CI检查失败
3. **AI生成** → Cursor规则拒绝

### 🛠️ 误操作补救

```bash
# 一键移动违规文件到正确位置
make move-clutter
```

### 📋 正确示例

```
❌ 错误：
├── README_v2.md (根目录)
├── test_utils.py (根目录)
└── temp_config.txt (根目录)

✅ 正确：
├── docs/00_product/README_v2.md
├── backend/apps/utils/tests/test_utils.py
└── docs/01_guideline/temp_config.txt
```
