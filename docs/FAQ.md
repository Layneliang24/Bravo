# 常见问题解答 (FAQ)

## 代码格式问题

### Q: 代码格式问题有什么影响？

#### 直接影响

- **可读性差**：格式混乱的代码难以阅读和理解
- **协作困难**：不同开发者习惯不同格式，容易产生冲突
- **审查效率低**：Reviewer 需要花时间理解格式，而不是关注逻辑

#### 间接影响

- **Git 历史污染**：格式修改会产生大量无意义的 diff
- **合并冲突**：格式不一致容易导致合并冲突
- **工具兼容性**：某些工具可能对格式敏感

#### 长期影响

- **代码质量感知**：格式混乱给人代码质量差的印象
- **新人上手难度**：新开发者需要适应不一致的格式
- **技术债务积累**：格式问题会越积越多

### Q: 如何解决历史文件的格式问题？

#### 一次性全量修复（推荐）

```bash
# 检查哪些文件有格式问题
npx prettier --list-different src/

# 一次性修复所有格式问题
npx prettier --write src/

# 提交修复
git add . && git commit -m "style: 修复历史文件prettier格式问题"
```

#### 预防性检查

```bash
# 定期检查
npx prettier --check .
```

### Q: pre-commit 钩子为什么只检查暂存区文件？

这是 pre-commit 的设计原理：

- **效率考虑**：避免每次提交都检查整个项目
- **逻辑合理**：已提交的文件理论上已经通过检查
- **开发体验**：开发者只需要关注自己修改的文件

**注意**：pre-commit 只能保证增量质量，不能保证存量质量。对于历史遗留问题，需要主动进行一次性清理。

### 解决方案记录

**问题**：历史文件跳过了 prettier 检查，导致格式不一致
**发现**：3个前端文件存在格式问题（30%的文件）
**解决**：使用 `npx prettier --write src/` 一次性修复
**结果**：所有文件格式统一，代码可读性提升
**时间**：2025-09-09

## 开发环境问题

### Q: Pre-commit检查持续失败，无法提交代码

**问题描述**: 遇到TypeScript和ESLint依赖问题导致pre-commit失败

**具体错误**:

1. `global-teardown.ts: Type 'IGlob' is missing properties` - glob API版本不兼容
2. `Cannot find module '@eslint/eslintrc/dist/eslintrc.cjs'` - ESLint依赖路径错误
3. Python pylint \_meta访问警告（可接受级别）

**尝试的解决方案**:

- 修复Python变量命名和导入问题 ✅
- 安装缺失的TypeScript类型定义 ✅
- 修复glob API使用方式 ❌ (API不兼容)
- 重新安装npm依赖 ❌ (权限问题)

**临时解决方案**:
当pre-commit阻止关键修复验证时，可以考虑：

```bash
# 仅在紧急情况下使用，之后必须修复质量问题
git commit --no-verify -m "紧急修复: 描述具体问题"
```

**根本解决方案**:

1. 升级到兼容的glob版本
2. 重建ESLint配置和依赖
3. 调整pylint配置忽略Django \_meta访问

**时间**: 2025-09-15

### Q: Vue.js TypeScript类型检查失败 - @vue/shared模块dist目录缺失

**问题描述**: dev分支CI失败，TypeScript类型检查无法通过

**具体错误**:

```
Error: Cannot find module './dist/shared.cjs.js'
Require stack:
- node_modules/@vue/shared/index.js
- node_modules/@vue/language-core/lib/utils/shared.js
- [Vue TypeScript chain...]
```

**根本原因**:
Vue.js `@vue/shared` 模块安装不完整，缺少 `dist` 目录，导致 `vue-tsc --noEmit` 命令失败

**真正原因**:

- **CI环境**: 没有npm缓存("npm cache is not found")，全新安装依赖，Vue模块完整
- **本地环境**: 有损坏的npm缓存/依赖，Vue模块缺少dist目录

**解决方案**:

1. **清除缓存并重新安装依赖** (本地环境):

```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

2. **ESLint配置优化** (已修复):

```javascript
// 测试文件中禁用命名规范检查，允许Vue组件kebab-case名称
files: ['**/*.test.{js,ts}', '**/*.spec.{js,ts}'],
rules: {
  '@typescript-eslint/naming-convention': 'off'
}
```

3. **Docker环境开发** (推荐):
   按照项目规范使用容器化环境，避免本地依赖问题

**修复记录**:

- **PR #26**: 成功合并到dev分支，修复了ESLint配置
- **根因确认**: CI失败是因为vue-tsc静默失败，不是真正的通过
- **本地验证**: 清除缓存后TypeScript检查通过
- **状态**: 问题已解决，需要触发新的CI验证修复效果

**时间**: 2025-09-15
