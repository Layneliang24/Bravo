# 🧹 后端技术债务清理建议

## 🎯 优化目标

统一测试配置，消除重复配置和混乱

## 📝 具体操作

### 1. 统一pytest配置

- **删除** `backend/pytest.ini`
- **保留** `backend/pyproject.toml` 中的pytest配置
- **合并** pytest-coverage.ini 到 pyproject.toml

### 2. 整合测试settings

- **保留** `test.py` 作为主要测试配置
- **评估** test_simple.py 和 test_sqlite.py 是否必要
- **建议** 使用环境变量区分不同测试场景

### 3. 清理覆盖率配置

- **删除** 单独的 pytest-coverage.ini
- **统一** 在 pyproject.toml 中配置覆盖率

## 💰 预期收益

- 减少配置文件数量 40%
- 消除配置冲突风险
- 简化维护复杂度
