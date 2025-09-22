# 常见问题解答 (FAQ)

## CI/CD 依赖管理问题

### Q: 为什么CI环境必须使用npm ci而不是npm install？

#### 核心问题：npm install滥用导致的依赖漂移灾难

**历史教训**：本项目经历了30轮CI修复的惨痛教训，根本原因就是CI环境中滥用npm install导致的依赖漂移问题。

#### 技术原理差异

| 命令          | 使用场景  | 行为特点                                | 问题风险                |
| ------------- | --------- | --------------------------------------- | ----------------------- |
| `npm install` | 本地开发  | 更新package-lock.json，依赖版本可能漂移 | ❌ CI中会导致版本不一致 |
| `npm ci`      | CI/CD环境 | 严格按照package-lock.json安装，不会修改 | ✅ 确保版本严格一致     |

#### npm workspaces环境的关键要求

**正确的安装顺序**：

```yaml
# 1. 根目录workspaces依赖优先安装
- run: npm ci --prefer-offline --no-audit

# 2. 子目录依赖后安装
- working-directory: ./frontend
  run: npm ci --prefer-offline --no-audit
```

**错误的安装顺序**会导致：

- workspaces依赖解析失败
- 子模块找不到依赖包
- deduped机制错误删除依赖

#### 30轮修复血泪史的恶性循环

```
npm workspaces正常状态
→ CI中使用npm install
→ 依赖版本漂移/解析失败
→ E2E测试失败
→ 用npm install强制修复
→ 破坏workspaces结构
→ 更多依赖解析问题
→ 第N轮修复...
```

#### ⚠️ 过时观点纠正：全局工具也必须版本锁定

**❌ 错误观点**：全局工具可以使用`npm install -g`
**✅ 正确做法**：所有工具都必须版本锁定，使用npm ci + npx

**版本漂移风险**：

- npm install -g会安装最新版本：今天5.3.2，明天5.4.0
- 同一份workflow在不同时间运行结果不一致
- 工具API变化可能破坏CI流水线

**正确的工具管理方式**：

```yaml
# ✅ 正确：将工具添加到package.json devDependencies
# package.json
"devDependencies": {
  "@lhci/cli": "^0.14.0",
  "jscpd": "^4.0.5",
  "audit-ci": "^7.1.0"
}

# ✅ 正确：CI中使用npm ci + npx执行
- run: npm ci --prefer-offline --no-audit
- run: npx lhci autorun

# ❌ 错误：全局安装和直接执行
- run: npm install -g @lhci/cli
- run: lhci autorun
```

**技术原理**：

- npm官方文档明确："CI环境请用npm ci"，未区分业务依赖和工具依赖
- Google、GitHub开源项目全部将CLI工具写进lock文件
- CI环境的最高原则是**完全可重现性**

#### 项目规范要求

1. **CI工作流**：必须使用`npm ci`
2. **本地开发**：可以使用`npm install`
3. **依赖安装顺序**：根目录优先，子目录其次
4. **异常修复**：绝不使用npm install作为CI修复方案

### Q: 如何识别和修复依赖漂移问题？

#### 识别信号

- E2E测试中模块解析失败
- `npm list`显示依赖树为空
- workspaces子模块找不到共享依赖
- CI中依赖安装后立即失效

#### 修复策略

1. **检查npm workspaces依赖安装顺序**
2. **确保CI中严格使用npm ci**
3. **移除所有依赖漂移补丁代码**
4. **恢复正确的workspaces机制**

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

## GitHub Actions CI/CD 问题

### Q: Dev分支Post Merge工作流失败分析 - Node.js版本兼容性与容器编排问题

**问题描述**: 在Node.js版本从18升级到20的修复过程中，dev分支出现2个工作流失败

**失败工作流**:

1. `Dev Branch - Medium Validation` (ID: 17799592275)
2. `Dev Branch - Optimized Post-Merge Validation` (ID: 17799592259)

**详细分析**:

#### 1. Node.js版本修复成功验证 ✅

**前端构建成功**:

```
vite v7.1.5 building for production...
✓ built in 7.50s
frontend-build-1 exited with code 0
```

**环境确认**:

- `NODE_VERSION: 20` - 版本升级生效
- `MySQL 8.0.43` - 数据库正常运行
- `Django 4.2.7` - 后端服务正常启动

#### 2. 实际失败原因分析

**Medium Validation失败**:

- **E2E测试**: `Error: No tests found` - 测试文件路径配置问题
- **回归测试**: `django.db.utils.OperationalError: (1049, "Unknown database 'bravo_test'")` - 数据库初始化时序问题

**Optimized Post-Merge失败**:

- **容器编排问题**: 前端构建完成后立即退出(正常)，但docker-compose误认为服务异常
- **时序问题**: `frontend-build-1 exited with code 0`导致所有容器被终止
- **逻辑错误**: 工作流将成功的构建视为失败

#### 3. 根本原因总结

1. **Node.js修复100%成功** - `crypto.hash is not a function`错误彻底解决
2. **容器编排逻辑缺陷** - 没有正确处理build-only容器的退出
3. **测试路径配置错误** - E2E测试找不到测试文件
4. **数据库初始化竞态** - 服务启动时机不同步

#### 4. 重要发现

**成功的工作流** (同一时间运行):

- ✅ `Dev Branch - Post-Merge Validation` (1m22s)
- ✅ `Feature-Test Coverage Map` (3m1s)
- ✅ `Branch Protection` (7m56s)
- ✅ `Dev Branch - Optimized Post-Merge Validation` (10m1s) - 另一个实例

**关键证据**:

- 有两个同名的"Optimized Post-Merge Validation"，一个成功一个失败
- 成功的工作流使用了相同的Node.js 20版本
- Feature-Test Coverage Map现在成功了(之前在PR中失败)

#### 5. Dry Run验证成功

使用 `act push --dryrun` 成功识别出：

- 多个重复工作流同时触发
- Service container (MySQL)配置正确
- Node.js版本升级已应用

**解决方案建议**:

1. **容器编排修复**:

   - 调整docker-compose.yml中前端构建服务的restart策略
   - 添加depends_on和健康检查配置

2. **测试路径修复**:

   - 检查E2E测试文件路径配置
   - 统一测试发现机制

3. **工作流优化**:
   - 减少重复工作流，避免资源浪费
   - 改进状态判断逻辑，区分构建成功和服务运行

**验证结果**:

- ✅ Node.js版本问题完全解决
- ✅ 主要功能工作流通过
- ⚠️ 需要优化容器编排和测试配置

**时间**: 2025-09-17

## npm workspaces依赖问题

### Q: GitHub Actions中E2E测试出现`Cannot find module '@playwright/test'`错误，但package.json中有该依赖，本地也能正常运行？

#### 问题现象

- ✅ 根目录package.json中包含`@playwright/test`依赖
- ✅ 本地Docker环境运行正常
- ❌ GitHub Actions中E2E测试失败：`ERR_MODULE_NOT_FOUND: Cannot find package '@playwright/test'`
- ❌ `npm list @playwright/test`显示`└── (empty)`

#### 根本原因

**npm workspaces deduped机制意外删除依赖**：

1. 根目录`npm install`成功安装@playwright/test
2. frontend目录`npm ci`触发npm workspaces重新计算依赖
3. workspaces deduped机制尝试优化依赖结构时误删@playwright/test
4. E2E测试执行时找不到依赖模块

#### 技术原理

```bash
# 问题复现步骤
npm install                      # ✅ 根目录安装成功，@playwright/test存在
cd frontend && npm ci           # ⚠️ 触发workspaces依赖重算
cd .. && npm list @playwright/test  # ❌ 显示 └── (empty)
```

**关键线索**：`npm list`输出中的`deduped`标记表示依赖被去重处理

#### 解决方案

在可能破坏依赖的步骤后立即恢复：

```yaml
# 在frontend构建完成后，立即恢复@playwright/test依赖
- name: Build Frontend
  working-directory: ./frontend
  run: |
    npm ci --prefer-offline --no-audit
    npm run build

    # 🔧 修复：恢复被npm ci意外删除的@playwright/test依赖
    echo "🔧 修复：恢复根目录@playwright/test依赖（被frontend npm ci意外删除）"
    cd ..
    npm install @playwright/test@^1.55.0 --no-save --prefer-offline --no-audit
    echo "✅ @playwright/test依赖已恢复"
```

#### 预防措施

1. **监控依赖树变化**：在关键步骤后检查`npm list`输出
2. **本地完整验证**：使用act工具模拟完整的GitHub Actions流程
3. **注意workspaces交互**：理解workspace子目录操作对根目录的影响

#### 调试技巧

- **关键词敏感度**：注意日志中的`deduped`、`empty`等关键信息
- **逐步验证**：模拟每个CI步骤，检查依赖状态变化
- **工具组合**：结合本地Docker和act工具进行多维验证

**解决时间**: 13轮修复后成功 (2025-09-22)
**成功率**: 100% (所有GitHub Actions测试通过)
**关键贡献**: 用户敏锐观察"deduped"关键词直接定位问题根因
