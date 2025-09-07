# 代码变更追踪系统 - 生产部署指南

## 系统概述

代码变更追踪系统是一个基于Git钩子的自动化工具，用于检测和防止临时修改标记（如TODO、FIXME、HACK等）被意外提交到生产环境。

### 核心功能
- **临时修改检测**: 自动识别代码中的临时标记
- **快速扫描**: 仅检查暂存文件，平均扫描时间0.02-0.03秒
- **智能拦截**: 根据严重性级别决定是否阻止提交
- **紧急绕过**: 支持--no-verify参数跳过检查

## 系统架构

```
.husky/
├── pre-commit          # Git钩子入口
scripts/
├── fast_pre_commit.py  # 快速检查脚本
├── pre_commit_monitor.py # 全量检查脚本（备用）
```

## 安装部署

### 前置条件
- Python 3.7+
- Git 2.9+
- Husky (已配置)

### 部署步骤

1. **确认文件完整性**
   ```bash
   # 检查关键文件是否存在
   ls -la .husky/pre-commit
   ls -la scripts/fast_pre_commit.py
   ```

2. **验证权限设置**
   ```bash
   # 确保钩子文件可执行
   chmod +x .husky/pre-commit
   chmod +x scripts/fast_pre_commit.py
   ```

3. **测试系统功能**
   ```bash
   # 创建测试文件
   echo "# TODO: 测试标记" > test_temp.py
   git add test_temp.py
   
   # 测试检查功能
   git commit -m "测试提交"
   
   # 清理测试文件
   git reset HEAD test_temp.py
   rm test_temp.py
   ```

## 使用指南

### 日常使用

系统会在每次`git commit`时自动运行，无需手动操作。

### 检测规则

#### 高严重性标记（会阻止提交）
- `TODO`: 待办事项
- `FIXME`: 需要修复的问题
- `HACK`: 临时解决方案
- `XXX`: 需要注意的问题
- `BUG`: 已知错误
- `TEMP`: 临时代码
- `DEBUG`: 调试代码
- `REMOVE`: 需要删除的代码

#### 中等严重性标记（会警告但不阻止）
- `NOTE`: 注释说明
- `REVIEW`: 需要审查
- `OPTIMIZE`: 性能优化点
- `REFACTOR`: 重构建议

### 紧急绕过机制

当需要紧急提交时，可以使用以下命令跳过检查：

```bash
git commit -m "紧急修复" --no-verify
```

**注意**: 仅在紧急情况下使用，建议后续创建issue跟踪临时修改。

## 配置管理

### 自定义检测规则

编辑`scripts/fast_pre_commit.py`文件中的规则配置：

```python
# 高严重性模式（阻止提交）
HIGH_SEVERITY_PATTERNS = [
    r'\b(TODO|FIXME|HACK|XXX|BUG|TEMP|DEBUG|REMOVE)\b',
    # 添加自定义规则
]

# 中等严重性模式（仅警告）
MEDIUM_SEVERITY_PATTERNS = [
    r'\b(NOTE|REVIEW|OPTIMIZE|REFACTOR)\b',
    # 添加自定义规则
]
```

### 文件类型过滤

```python
# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.vue',
    '.java', '.cpp', '.c', '.h', '.cs', '.php',
    '.rb', '.go', '.rs', '.swift', '.kt'
}
```

## 故障排除

### 常见问题

#### 1. 编码错误
**症状**: `UnicodeEncodeError`或乱码输出
**解决方案**:
```bash
# 设置环境变量
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
```

#### 2. 权限错误
**症状**: `Permission denied`
**解决方案**:
```bash
chmod +x .husky/pre-commit
chmod +x scripts/fast_pre_commit.py
```

#### 3. Python路径问题
**症状**: `python: command not found`
**解决方案**:
```bash
# 检查Python安装
which python3
# 或修改钩子文件中的python路径
```

#### 4. 钩子未触发
**症状**: 提交时没有检查输出
**解决方案**:
```bash
# 重新安装husky
npx husky install
# 检查钩子文件内容
cat .husky/pre-commit
```

### 调试模式

启用详细输出进行调试：

```bash
# 手动运行检查脚本
python scripts/fast_pre_commit.py --debug

# 查看Git钩子日志
GIT_TRACE=1 git commit -m "测试"
```

### 性能监控

系统会输出扫描时间，正常情况下应在0.1秒以内：

```
[INFO] 快速提交前检查启动
[INFO] 扫描 X 个暂存文件，耗时 0.03 秒
[RESULT] 发现 Y 个问题
```

如果扫描时间过长，检查：
1. 暂存文件数量是否过多
2. 文件大小是否异常
3. 正则表达式是否过于复杂

## 监控和维护

### 使用统计

系统会记录以下信息：
- 检查次数
- 发现问题数量
- 阻止提交次数
- 平均扫描时间

### 定期维护

1. **每月检查**
   - 验证系统正常运行
   - 更新检测规则
   - 清理日志文件

2. **季度评估**
   - 分析使用统计
   - 优化检测规则
   - 团队培训更新

## 团队协作

### 最佳实践

1. **代码审查**: 在PR中关注临时标记
2. **文档更新**: 及时更新相关文档
3. **问题跟踪**: 为临时修改创建对应issue
4. **定期清理**: 定期清理已完成的临时标记

### 培训要点

1. 系统工作原理
2. 检测规则说明
3. 紧急绕过使用场景
4. 故障排除基础

## 版本历史

- **v1.0.0**: 初始版本，基础检测功能
- **v1.1.0**: 添加快速扫描模式
- **v1.2.0**: 优化编码兼容性
- **v1.3.0**: 生产环境部署版本

## 支持联系

如遇到问题，请：
1. 查阅本文档故障排除部分
2. 检查系统日志和错误信息
3. 联系开发团队获取支持

---

*最后更新: 2024年1月*
*文档版本: v1.0*