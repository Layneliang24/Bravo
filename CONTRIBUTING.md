# 贡献指南

感谢您对 Bravo 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

- 使用 GitHub Issues 报告 bug
- 提供详细的复现步骤
- 包含环境信息（操作系统、Python/Node.js 版本等）

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add some amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 遵循项目的代码风格
- 添加适当的测试
- 更新相关文档
- 确保所有测试通过

## 开发环境设置

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py runserver
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test

# E2E 测试
cd e2e
npm run test
```

## 提交信息规范

我们使用约定式提交规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：

```
feat: add user authentication system
fix: resolve login redirect issue
docs: update API documentation
```

## 代码审查

所有提交的代码都会经过代码审查：

- 确保代码质量
- 检查安全性
- 验证测试覆盖率
- 确认文档更新

## 问题讨论

- 使用 GitHub Discussions 进行功能讨论
- 使用 GitHub Issues 报告 bug
- 通过邮件联系维护者

感谢您的贡献！
