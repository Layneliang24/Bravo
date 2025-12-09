# API契约文档目录

本目录包含项目的所有API契约文档，遵循OpenAPI 3.0规范。

## 📁 目录结构

```
api-contracts/
├── README.md                           # 本文档
├── REQ-2025-EXAMPLE-demo/              # 示例API契约
│   └── api.yaml
└── REQ-2025-003-user-login/            # 用户登录功能API契约
    └── REQ-2025-003-user-login-api.yaml
```

## 📋 API契约文档规范

### 文件命名规范

- **目录名**：`REQ-{YYYY}-{NNN}-{feature-name}`
- **文件名**：`REQ-{YYYY}-{NNN}-{feature-name}-api.yaml`

例如：
- 目录：`REQ-2025-003-user-login/`
- 文件：`REQ-2025-003-user-login-api.yaml`

### 文档结构

每个API契约文档应包含：

1. **基本信息** (`info`)：标题、版本、描述
2. **服务器配置** (`servers`)：开发/测试/生产环境URL
3. **API路径** (`paths`)：所有API端点定义
4. **组件定义** (`components`)：
   - `schemas`：请求/响应模型
   - `securitySchemes`：安全认证方案
   - `responses`：通用响应定义
   - `parameters`：通用参数定义

### OpenAPI 3.0规范

所有文档必须符合 [OpenAPI 3.0 规范](https://swagger.io/specification/)。

## 🔗 访问API文档

### 1. Swagger UI（交互式文档）

访问地址：
- **本地开发**：http://localhost:8000/api/docs/
- **开发环境**：https://dev.layneliang.com/api/docs/
- **生产环境**：https://layneliang.com/api/docs/

**功能特性**：
- ✅ 交互式API测试
- ✅ 实时请求/响应示例
- ✅ JWT Token认证支持
- ✅ 自动生成的文档（基于代码）

### 2. ReDoc（美观的文档）

访问地址：
- **本地开发**：http://localhost:8000/api/redoc/
- **开发环境**：https://dev.layneliang.com/api/redoc/
- **生产环境**：https://layneliang.com/api/redoc/

**功能特性**：
- ✅ 三栏布局，阅读体验优秀
- ✅ 自动生成的文档（基于代码）

### 3. OpenAPI Schema（JSON格式）

访问地址：
- **本地开发**：http://localhost:8000/api/schema/
- **开发环境**：https://dev.layneliang.com/api/schema/
- **生产环境**：https://layneliang.com/api/schema/

**用途**：
- ✅ 导入到Postman/Insomnia
- ✅ 生成Mock Server
- ✅ CI/CD自动化测试

### 4. 静态契约文档（本目录下的YAML文件）

**位置**：`docs/01_guideline/api-contracts/{REQ-ID}/{REQ-ID}-api.yaml`

**用途**：
- ✅ 版本控制和变更追踪
- ✅ 前后端协作的参考文档
- ✅ 设计阶段的API规范定义
- ✅ 手动导入到API工具

## 🛠️ 使用场景

### 场景1：前后端并行开发

**流程**：
1. 后端架构师根据PRD设计API契约（OpenAPI YAML）
2. 前端基于契约文档创建Mock Server
3. 前端独立开发，不依赖后端实现
4. 后端按照契约实现API
5. 契约测试验证前后端一致性

**工具推荐**：
- **Mock Server**：使用 [Prism](https://stoplight.io/open-source/prism) 基于OpenAPI文档生成Mock API
- **前端开发**：直接调用Mock API，无需等待后端

```bash
# 安装Prism
npm install -g @stoplight/prism-cli

# 启动Mock Server
prism mock docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml
```

### 场景2：API测试

**使用Postman导入**：
1. 打开Postman
2. Import → Link
3. 输入：`http://localhost:8000/api/schema/`
4. 自动导入所有API端点

### 场景3：文档同步验证

**验证静态文档与代码实现的一致性**：

```bash
# 生成当前代码的OpenAPI Schema
python manage.py spectacular --file schema-from-code.json

# 对比静态文档
diff schema-from-code.json docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml
```

## 📝 创建新API契约文档

### 步骤1：创建目录

```bash
mkdir -p docs/01_guideline/api-contracts/REQ-2025-XXX-feature-name
```

### 步骤2：创建OpenAPI文档

参考 `REQ-2025-EXAMPLE-demo/api.yaml` 或 `REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml`

### 步骤3：更新PRD

在PRD的frontmatter中添加：

```yaml
api_contract: docs/01_guideline/api-contracts/REQ-2025-XXX-feature-name/REQ-2025-XXX-feature-name-api.yaml
```

### 步骤4：验证文档

```bash
# YAML语法验证
python -c "import yaml; yaml.safe_load(open('docs/01_guideline/api-contracts/REQ-2025-XXX-feature-name/REQ-2025-XXX-feature-name-api.yaml', encoding='utf-8'))"

# 使用Swagger Editor在线验证
# 访问：https://editor.swagger.io/
```

## 🔍 当前API契约文档列表

| REQ-ID | 功能 | 文档路径 | 状态 |
|--------|------|----------|------|
| REQ-2025-003 | 用户登录认证 | `REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml` | ✅ 已完成 |
| REQ-2025-EXAMPLE | 示例文档 | `REQ-2025-EXAMPLE-demo/api.yaml` | 📝 示例 |

## ⚠️ 重要提示

1. **契约文档优先**：在实现API之前，应先创建API契约文档
2. **保持同步**：代码实现变更时，应及时更新契约文档
3. **版本控制**：所有契约文档都应纳入Git版本控制
4. **审查机制**：重要API的契约文档应经过团队审查

## 📚 相关文档

- [OpenAPI 3.0 规范](https://swagger.io/specification/)
- [drf-spectacular 文档](https://drf-spectacular.readthedocs.io/)
- [Prism Mock Server](https://stoplight.io/open-source/prism)

## 🔧 技术栈

- **文档生成工具**：`drf-spectacular` (Django REST Framework)
- **文档格式**：OpenAPI 3.0 (YAML)
- **交互式文档**：Swagger UI / ReDoc
- **Mock Server**：Prism


