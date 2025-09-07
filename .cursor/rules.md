# Cursor AI 编程规则与约束

## 🔒 功能-测试映射锁

### 强制规则

1. **测试文件必须映射功能**
   - 写完任何测试后，必须在文件顶部调用 `linkTestToFeature('功能ID')`
   - 或使用 `describeFeature('功能ID', '描述', testFn)` 包装测试套件
   - 不允许把 `linkTestToFeature` 指向不存在的功能ID

2. **功能ID验证**
   - 所有功能ID必须在 `features.json` 中定义
   - 格式必须为 `[A-Z]+-\d+` (如: `ENG-001`, `BLOG-002`)
   - CI会检查每个功能ID是否至少被一条测试映射；缺了就失败

3. **测试文件结构要求**
   ```javascript
   // ✅ 正确示例
   const { linkTestToFeature } = require('../testMap');
   
   // 在文件顶部声明覆盖的功能
   linkTestToFeature('ENG-001');
   
   describe('英语新闻列表', () => {
     it('should display news titles and summaries', () => {
       // 测试代码
     });
   });
   ```

   ```javascript
   // ✅ 或使用 describeFeature
   const { describeFeature } = require('../testMap');
   
   describeFeature('ENG-001', '英语新闻列表页显示标题和摘要', () => {
     it('should display news titles', () => {
       // 测试代码
     });
   });
   ```

4. **多功能映射**
   ```javascript
   // ✅ 一个测试文件覆盖多个功能
   linkTestToFeature('ENG-001');
   linkTestToFeature('ENG-002');
   
   // 或批量映射
   linkMultipleFeatures(['ENG-001', 'ENG-002']);
   ```

## 📋 功能清单管理

### features.json 结构
```json
{
  "id": "ENG-001",
  "desc": "英语新闻列表页显示标题和摘要",
  "category": "english",
  "priority": "high",
  "components": ["NewsList.vue", "NewsCard.vue"],
  "apis": ["/api/english/news/"],
  "status": "active"
}
```

### 新功能开发流程
1. 先在 `features.json` 中添加功能定义
2. 实现功能代码
3. 编写测试并调用 `linkTestToFeature`
4. 运行 `npm run test:coverage` 验证映射

## 🧪 测试编写规范

### 覆盖率要求
- **全局最低**: 90% (lines, statements, functions, branches)
- **组件目录**: 95%
- **工具函数**: 100%
- **视图页面**: 85%

### 测试类型映射
```javascript
// 单元测试
linkTestToFeature('COMMON-001'); // 通用组件

// 集成测试
linkTestToFeature('ENG-001'); // 英语功能
linkTestToFeature('BLOG-001'); // 博客功能

// E2E测试
linkTestToFeature('USER-001'); // 用户流程
```

### 测试命名规范
```javascript
// ✅ 好的测试描述
describe('[ENG-001] 英语新闻列表', () => {
  it('should display 10 news items per page', () => {});
  it('should show loading state while fetching', () => {});
  it('should handle API errors gracefully', () => {});
});

// ❌ 避免的测试描述
describe('News component', () => {
  it('works', () => {}); // 太模糊
});
```

## 🚫 禁止行为

1. **绕过测试映射**
   - 不允许创建没有 `linkTestToFeature` 的测试文件
   - 不允许使用无效的功能ID
   - 不允许删除现有的功能映射

2. **降低覆盖率**
   - 不允许修改 `jest.config.js` 中的覆盖率阈值
   - 不允许在 `collectCoverageFrom` 中排除新文件
   - 不允许使用 `/* istanbul ignore */` 除非有充分理由

3. **跳过CI检查**
   - 不允许修改 `.github/workflows/` 中的测试步骤
   - 不允许在CI失败时强制合并PR
   - 不允许禁用功能覆盖率验证

## 🔧 开发工具集成

### VS Code 设置
```json
{
  "jest.autoRun": "watch",
  "jest.showCoverageOnLoad": true,
  "jest.coverageFormatter": "GutterFormatter"
}
```

### 快捷命令
```bash
# 运行带功能映射的测试
npm run test:coverage

# 验证功能覆盖率
npm run test:coverage-verify

# 生成功能-测试地图
node scripts/buildFeatureMap.js

# 检查未覆盖功能
npm run feature:uncovered
```

## 📊 质量门控

### PR合并要求
1. ✅ 所有测试通过
2. ✅ 代码覆盖率 ≥ 90%
3. ✅ 功能覆盖率 ≥ 70%
4. ✅ 没有未映射的测试文件
5. ✅ 没有无效的功能ID引用
6. ✅ Lighthouse性能评分 ≥ 90

### 自动化检查
- GitHub Actions 会在每次PR时验证所有规则
- 覆盖率报告会自动生成并评论到PR
- 功能-测试地图会实时更新

## 🎯 最佳实践

### 测试驱动开发 (TDD)
1. 在 `features.json` 中定义功能
2. 编写失败的测试 + `linkTestToFeature`
3. 实现最小可行代码
4. 重构并保持测试通过

### 功能分解
```javascript
// ✅ 细粒度功能映射
linkTestToFeature('ENG-001'); // 列表显示
linkTestToFeature('ENG-002'); // 翻译功能
linkTestToFeature('ENG-003'); // 打字练习

// ❌ 避免过于宽泛
linkTestToFeature('ENG-ALL'); // 太宽泛
```

### 错误处理
```javascript
// ✅ 测试错误场景
describeFeature('ENG-001', '新闻列表', () => {
  it('should handle network errors', () => {});
  it('should show empty state when no data', () => {});
  it('should retry failed requests', () => {});
});
```

## 🚨 违规处理

如果违反以上规则：
1. **CI自动失败** - PR无法合并
2. **覆盖率下降** - 自动阻止部署
3. **功能未映射** - 生成警告报告
4. **质量门控** - 需要手动审查

---

**记住**: 这些规则是为了确保代码质量和功能完整性。每个测试都应该有明确的功能映射，每个功能都应该有充分的测试覆盖。