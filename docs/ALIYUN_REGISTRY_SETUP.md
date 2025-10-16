# 阿里云容器镜像服务配置指南

## 📋 前置准备

本文档指导您完成阿里云容器镜像服务的配置，用于存储和分发Docker镜像。

---

## 步骤1：开通阿里云容器镜像服务

1. 登录阿里云控制台：https://cr.console.aliyun.com/
2. 选择 **个人实例（免费）** 或 **企业版实例**
3. 建议选择 **杭州（华东1）** 区域（与服务器同区，加速拉取）

---

## 步骤2：创建命名空间

1. 进入容器镜像服务控制台
2. 左侧菜单选择 **命名空间**
3. 点击 **创建命名空间**：
   - **命名空间名称**: `bravo-project`
   - **访问权限**: 私有（Private）
   - 点击 **确定**

---

## 步骤3：创建镜像仓库

### 3.1 创建Backend仓库

1. 左侧菜单选择 **镜像仓库**
2. 点击 **创建镜像仓库**
3. 填写信息：
   - **命名空间**: `bravo-project`
   - **仓库名称**: `backend`
   - **仓库类型**: 私有
   - **摘要**: Django Backend服务
   - **仓库类型**: 本地仓库
4. 代码源：选择 **本地仓库**（不绑定代码源）
5. 点击 **创建**

### 3.2 创建Frontend仓库

1. 点击 **创建镜像仓库**
2. 填写信息：
   - **命名空间**: `bravo-project`
   - **仓库名称**: `frontend`
   - **仓库类型**: 私有
   - **摘要**: Vue Frontend + Nginx
   - **仓库类型**: 本地仓库
3. 点击 **创建**

---

## 步骤4：获取访问凭证

### 4.1 设置固定密码

1. 进入容器镜像服务控制台
2. 左侧菜单选择 **访问凭证**
3. 点击 **设置Registry登录密码**
4. 设置一个强密码（至少8位，包含大小写字母和数字）
5. 记录以下信息：
   ```
   仓库地址: registry.cn-hangzhou.aliyuncs.com
   用户名: 你的阿里云账号（通常是邮箱或手机号）
   密码: 刚刚设置的Registry密码
   ```

### 4.2 测试登录

在本地测试（可选）：

```bash
docker login registry.cn-hangzhou.aliyuncs.com
# 输入用户名和密码
```

---

## 步骤5：配置GitHub Secrets

1. 进入GitHub仓库：https://github.com/Layneliang24/Bravo
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下secrets：

### 5.1 ALIYUN_REGISTRY_USERNAME

- **Name**: `ALIYUN_REGISTRY_USERNAME`
- **Value**: 你的阿里云账号用户名
- 点击 **Add secret**

### 5.2 ALIYUN_REGISTRY_PASSWORD

- **Name**: `ALIYUN_REGISTRY_PASSWORD`
- **Value**: 你的Registry登录密码
- 点击 **Add secret**

---

## 步骤6：验证配置

### 6.1 检查命名空间和仓库

访问控制台确认创建成功：

- 命名空间: `bravo-project`
- 仓库:
  - `registry.cn-hangzhou.aliyuncs.com/bravo-project/backend`
  - `registry.cn-hangzhou.aliyuncs.com/bravo-project/frontend`

### 6.2 验证GitHub Secrets

在GitHub仓库的Settings页面确认secrets已添加：

- ✅ ALIYUN_REGISTRY_USERNAME
- ✅ ALIYUN_REGISTRY_PASSWORD

---

## 镜像Tag策略

### Dev环境（dev分支）

```
registry.cn-hangzhou.aliyuncs.com/bravo-project/backend:dev
registry.cn-hangzhou.aliyuncs.com/bravo-project/backend:dev-<short-sha>
registry.cn-hangzhou.aliyuncs.com/bravo-project/frontend:dev
registry.cn-hangzhou.aliyuncs.com/bravo-project/frontend:dev-<short-sha>
```

### Production环境（main分支）

```
registry.cn-hangzhou.aliyuncs.com/bravo-project/backend:latest
registry.cn-hangzhou.aliyuncs.com/bravo-project/backend:2025.01.15-a1b2c3d4
registry.cn-hangzhou.aliyuncs.com/bravo-project/frontend:latest
registry.cn-hangzhou.aliyuncs.com/bravo-project/frontend:2025.01.15-a1b2c3d4
```

---

## 常见问题

### Q: 忘记Registry密码怎么办？

A: 在控制台 **访问凭证** 页面点击 **重置Docker登录密码**

### Q: 镜像拉取很慢？

A:

1. 确保使用与服务器同区域的仓库（杭州）
2. 考虑使用企业版实例（更快的带宽）
3. 检查服务器网络配置

### Q: 登录失败 "unauthorized"?

A:

1. 检查用户名是否正确（通常是完整的阿里云账号）
2. 确认密码是Registry密码而非阿里云登录密码
3. 尝试重置Registry密码

### Q: GitHub Actions构建失败？

A: 检查Secrets配置：

```bash
# 在workflow中添加调试（不要暴露真实密码）
echo "Username length: ${#REGISTRY_USERNAME}"
echo "Password length: ${#REGISTRY_PASSWORD}"
```

---

## 🎉 完成

配置完成后，CI/CD流程将自动：

1. 在代码合并到dev/main后构建镜像
2. 推送镜像到阿里云仓库
3. 部署时从阿里云拉取镜像（无需服务器构建）

**优势**：

- ✅ 节省服务器内存和CPU资源
- ✅ 部署速度更快
- ✅ 支持镜像版本管理和回滚
- ✅ dev和prod环境完全隔离

---

**配置完成后，请通知开发人员继续下一步测试。**
