# 代码变更追踪系统使用指南

## 概述

本系统旨在解决开发过程中临时修改未还原导致的功能缺失问题，通过自动化监控和验证机制确保代码质量。

## 核心组件

### 1. 综合代码管理器 (`comprehensive_code_manager.py`)

主要功能：

- 创建项目基线
- 验证当前状态
- 生成综合报告

```bash
# 创建基线
python scripts/comprehensive_code_manager.py create-baseline

# 验证当前状态
python scripts/comprehensive_code_manager.py
```

### 2. 临时修改检测器 (`temp_modification_detector.py`)

自动扫描代码中的临时标记：

- TODO、FIXME、HACK等标记
- 注释掉的代码块
- 临时调试代码

```bash
# 扫描临时修改
python scripts/temp_modification_detector.py
```

### 3. 提交前监控 (`pre_commit_monitor.py`)

在代码提交前进行综合检查：

- Git状态检查
- 临时修改扫描
- 测试结果验证
- 功能完整性检查

```bash
# 提交前检查
python scripts/pre_commit_monitor.py
```

### 4. 代码还原验证器 (`code_restoration_validator.py`)

验证代码修改的合理性：

- 创建功能基线
- 对比验证
- 生成还原报告

```bash
# 创建基线
python scripts/code_restoration_validator.py create-baseline

# 验证还原
python scripts/code_restoration_validator.py validate
```

## 工作流程

### 日常开发流程

1. **开始开发前**

   ```bash
   # 创建当前状态基线
   python scripts/comprehensive_code_manager.py create-baseline
   ```

2. **开发过程中**

   - 使用规范的临时标记（TODO、FIXME等）
   - 定期运行临时修改检测

   ```bash
   python scripts/temp_modification_detector.py
   ```

3. **提交代码前**

   ```bash
   # 运行提交前检查
   python scripts/pre_commit_monitor.py
   ```

4. **根据检查结果采取行动**
   - **LOW风险**: 可以安全提交
   - **MEDIUM风险**: 谨慎操作，建议记录变更
   - **HIGH风险**: 需要解决问题后再提交
   - **CRITICAL风险**: 禁止提交，必须修复

### 问题排查流程

1. **发现功能缺失时**

   ```bash
   # 生成综合报告
   python scripts/comprehensive_code_manager.py

   # 检查临时修改
   python scripts/temp_modification_detector.py
   ```

2. **分析报告内容**

   - 查看 `docs/02_test_report/comprehensive_code_report.md`
   - 查看 `docs/02_test_report/temp_modifications_report.md`
   - 查看 `docs/02_test_report/pre_commit_report.md`

3. **定位问题代码**
   - 根据报告中的文件路径和行号
   - 重点关注高风险和中风险的修改

## 报告解读

### 风险等级说明

- **LOW**: 项目状态良好，可以正常开发
- **MEDIUM**: 存在一些需要注意的问题，建议谨慎操作
- **HIGH**: 发现重要问题，需要及时处理
- **CRITICAL**: 存在严重问题，必须立即修复

### 临时修改类型

- **TODO**: 待完成的功能
- **FIXME**: 需要修复的问题
- **HACK**: 临时解决方案
- **XXX**: 需要特别注意的代码
- **REMOVE**: 标记为删除的代码
- **DEBUG**: 调试代码
- **TEMP**: 临时代码

## 最佳实践

### 1. 规范使用临时标记

```python
# 好的做法
# TODO: 实现用户权限验证逻辑
# FIXME: 修复并发访问时的数据竞争问题
# HACK: 临时绕过API限制，需要在v2.0中正式解决

# 避免的做法
# 这里有问题
# 先这样写
# 临时注释
```

### 2. 定期清理临时修改

- 每周运行一次临时修改检测
- 及时处理高风险和中风险的修改
- 在功能完成后清理相关的TODO标记

### 3. 提交前必检

- 始终在提交前运行 `pre_commit_monitor.py`
- 根据风险等级决定是否提交
- 在提交信息中说明重要变更

### 4. 团队协作

- 团队成员都应了解并使用这套系统
- 在代码审查时关注临时修改报告
- 建立定期的代码质量检查会议

## 配置说明

### 排除规则

系统会自动排除以下文件：

- `node_modules/`、`venv/`等依赖目录
- `.git/`、`.vscode/`等配置目录
- `*.log`、`*.tmp`等临时文件
- 二进制文件和图片文件

### 自定义配置

可以通过修改脚本中的配置来适应项目需求：

- 调整风险等级阈值
- 添加新的临时标记类型
- 修改排除规则

## 故障排除

### 常见问题

1. **Unicode编码错误**

   - 确保终端支持UTF-8编码
   - 使用Git Bash或支持Unicode的终端

2. **权限问题**

   - 确保有读写项目目录的权限
   - 检查Git仓库状态

3. **依赖缺失**
   - 确保Python环境正确
   - 安装必要的依赖包

### 获取帮助

如果遇到问题，可以：

1. 查看生成的报告文件
2. 检查终端输出的错误信息
3. 确认项目结构和文件权限
4. 联系开发团队获取支持

## 总结

这套代码变更追踪系统通过自动化监控和验证，有效防止了临时修改导致的功能缺失问题。正确使用这套工具，可以显著提高代码质量和开发效率。
