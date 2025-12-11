# CI/CD 工作流架构优化方案

## 问题分析

### 1. workflow_run headBranch 问题

**问题**：

- `workflow_run` 触发时，工作流文件本身在触发时确定，使用的是触发工作流的 `headBranch` 版本
- 如果构建工作流从错误的分支触发，部署工作流会使用错误的工作流文件版本

**解决方案**：

- 在 `if` 条件中添加 `head_branch` 检查，确保只有从正确分支触发的构建工作流才会触发部署
- dev 部署：只从 dev 分支触发
- 生产部署：只从 main 分支触发

### 2. 镜像标签策略问题

**问题**：

- 当前使用可变标签（`dev`、`latest`），可能导致部署旧代码
- 可变标签可能被覆盖，无法确保100%是新代码

**解决方案**：

- **主要标签**：使用 Commit SHA（不可变，确保100%是新代码）
  - 生产环境：`${FULL_SHA}`
  - 开发环境：`dev-${FULL_SHA}`
- **辅助标签**：保留 `latest`、`dev`、`prod-stable`、`dev-stable`（用于快速引用）
- **部署策略**：优先使用 Commit SHA 标签，如果不存在则回退到辅助标签

## 工作流架构

### 分支策略

```
dev 分支 → 构建镜像 → 部署到开发环境
main 分支 → 构建镜像 → 部署到生产环境
```

### 工作流流程

1. **构建工作流** (`build-and-push-images.yml`)

   - 触发：dev 或 main 分支 push
   - 功能：构建并推送 Docker 镜像
   - 标签策略：
     - 生产环境：`${FULL_SHA}`, `latest`, `prod-stable`
     - 开发环境：`dev-${FULL_SHA}`, `dev`, `dev-stable`

2. **开发环境部署** (`deploy-dev.yml`)

   - 触发：构建工作流完成（仅从 dev 分支）
   - 功能：部署到开发服务器
   - 镜像标签：优先使用 `dev-${BUILD_SHA}`，回退到 `dev`

3. **生产环境部署** (`deploy-production.yml`)
   - 触发：构建工作流完成（仅从 main 分支）
   - 功能：部署到生产服务器
   - 镜像标签：优先使用 `${BUILD_SHA}`，回退到 `latest`

## 改进点

### 1. 分支隔离

```yaml
# deploy-dev.yml
if: ${{ github.event_name == 'workflow_dispatch' || (github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'dev') }}

# deploy-production.yml
if: ${{ github.event_name == 'workflow_dispatch' || (github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.head_branch == 'main') }}
```

### 2. Commit SHA 标签

```yaml
# build-and-push-images.yml
# 生产环境
BACKEND_TAGS="${REGISTRY}/${NAMESPACE}/backend:${FULL_SHA},${REGISTRY}/${NAMESPACE}/backend:latest,${REGISTRY}/${NAMESPACE}/backend:prod-stable"

# 开发环境
BACKEND_TAGS="${REGISTRY}/${NAMESPACE}/backend:dev-${FULL_SHA},${REGISTRY}/${NAMESPACE}/backend:dev,${REGISTRY}/${NAMESPACE}/backend:dev-stable"
```

### 3. 部署时使用 Commit SHA

```bash
# 获取构建工作流的Commit SHA
BUILD_SHA="${{ github.event.workflow_run.head_sha }}"

# 优先使用Commit SHA标签，回退到辅助标签
IMAGE_TAG=${BUILD_SHA} docker-compose pull || IMAGE_TAG=latest docker-compose pull
```

## 优势

1. **100% 代码确定性**：使用 Commit SHA 标签确保部署的代码与构建时的代码完全一致
2. **分支隔离**：dev 和 main 分支的部署完全隔离，不会互相影响
3. **回退机制**：如果 Commit SHA 标签不存在，自动回退到辅助标签
4. **可追溯性**：每个部署都有明确的 Commit SHA，便于追踪和回滚

## 参考文档

- [GitHub Actions: workflow_run](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [Docker 最佳实践：使用不可变标签](https://docs.docker.com/develop/dev-best-practices/tagging/)
