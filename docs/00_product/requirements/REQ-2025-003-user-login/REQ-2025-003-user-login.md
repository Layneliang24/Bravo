---req_id: REQ-2025-003-user-login
title: Bravo网站登录页面设计
status: approved
priority: high
type: feature
created_at: 2025-12-03 10:00:00+00:00
updated_at: 2025-12-30T10:00:00Z
author: human
refined_by: claude-opus-4
testcase_file: docs/00_product/requirements/REQ-2025-003-user-login/REQ-2025-003-user-login-test-cases.csv
testcase_status:
  total_cases: 65
  p0_cases: 12
  p1_cases: 42
  p2_cases: 11
  p3_cases: 0
  reviewed: true
  reviewed_by:
  - cursor-ai
  reviewed_at: 2025-12-13 00:00:00+00:00
test_files:
- backend/tests/unit/test_auth_models.py
- backend/tests/unit/test_auth_preview.py
- backend/tests/unit/test_captcha.py
- backend/tests/integration/test_captcha_api.py
- backend/tests/integration/test_email_verification_api.py
- backend/tests/integration/test_login_api.py
- backend/tests/integration/test_password_reset.py
- backend/tests/integration/test_preview_throttling.py
- backend/tests/integration/test_register_api.py
- backend/tests/integration/test_token_api.py
- e2e/tests/auth/test-captcha-refresh.spec.ts
- e2e/tests/auth/test-captcha-realtime-validation.spec.ts
- e2e/tests/auth/test-email-verification.spec.ts
- e2e/tests/auth/test-login-preview.spec.ts
- e2e/tests/auth/test-password-reset.spec.ts
- e2e/tests/auth/test-preview-ui-details.spec.ts
- e2e/tests/auth/test-register-accessibility.spec.ts
- e2e/tests/auth/test-register-button.spec.ts
- e2e/tests/auth/test-ui-animations.spec.ts
- e2e/tests/auth/test-ui-design.spec.ts
- frontend/src/components/auth/__tests__/LoginForm.spec.ts
- frontend/src/components/auth/__tests__/LoginForm-glass.spec.ts
- frontend/src/components/auth/__tests__/RegisterForm.spec.ts
- frontend/src/components/auth/__tests__/Captcha.spec.ts
- frontend/src/views/__tests__/Login.spec.ts
- frontend/src/views/__tests__/Register.spec.ts
- frontend/src/views/__tests__/ForgotPassword.spec.ts
- frontend/src/views/__tests__/ResetPassword.spec.ts
- frontend/src/views/__tests__/VerifyEmailView.spec.ts
- frontend/src/router/index.spec.ts
implementation_files:
- backend/apps/users/models.py
- backend/apps/users/views.py
- backend/apps/users/serializers.py
- backend/apps/users/utils.py
- backend/apps/users/throttling.py
- frontend/src/views/Login.vue
- frontend/src/components/auth/LoginForm.vue
- frontend/src/components/auth/RegisterForm.vue
- frontend/src/components/auth/PasswordResetForm.vue
- frontend/src/components/auth/Captcha.vue
- frontend/src/components/auth/UserPreview.vue
- frontend/src/components/auth/DefaultAvatar.vue
- frontend/src/stores/auth.ts
- frontend/src/api/auth.ts
api_contract: docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml
figma_design: https://www.figma.com/design/n7oYkASiqv2vgBpix0X9mi/Login-register-V1.0?node-id=0-1
deletable: false
---

# REQ-2025-003-user-login: Bravo网站登录页面设计

## 原始需求

登录网址页面设计，提供登录注册功能，以及动态验证码，密码找回，验证码刷新等等，现代风格UI设计，悬浮式输入框，不要使用通用的AI配色方案。

## 功能概述

设计并实现一个现代化的用户认证系统，包括登录、注册、密码找回、邮箱验证、动态验证码等功能。采用现代UI设计风格，使用悬浮式输入框，提供流畅的用户体验。

## 业务背景

用户认证是网站的核心功能，需要提供安全、便捷、美观的登录体验。现代用户对UI设计要求较高，需要避免千篇一律的AI生成配色方案，打造独特的品牌视觉风格。

## 开发方法论

### TDD（测试驱动开发）

本项目**必须**采用TDD（Test-Driven Development）开发方法论，严格遵循以下流程：

1. **红（Red）**：先编写失败的测试用例
2. **绿（Green）**：编写最少量的代码使测试通过
3. **重构（Refactor）**：优化代码结构，保持测试通过

### 任务组织原则

- **每个功能模块**必须按以下顺序组织任务：

  1. 编写单元测试（预期失败）
  2. 实现功能代码（使测试通过）
  3. 编写集成测试
  4. 重构和优化

- **后端先于前端**：后端API开发完成并通过测试后，再开发前端
- **测试覆盖率**：代码覆盖率必须 >= 80%
- **禁止跳过测试**：不允许先实现功能后补测试

### 已有项目约束

本项目是在**已有项目基础上扩展**，不是从零开始：

- Django项目已初始化，无需重新创建
- Vue 3项目已初始化，无需重新创建
- 已有`backend/apps/users/`目录和基础User模型
- 已有`frontend/src/views/Login.vue`页面

任务应聚焦于**扩展和增强**现有代码，而非重新初始化项目。

## 用户故事

### US-1: 用户登录

作为一个已注册用户，我希望能够使用邮箱和密码登录，以便访问我的账户。

### US-2: 用户注册

作为一个新用户，我希望能够注册账户，以便使用网站服务。

### US-3: 密码找回

作为一个忘记密码的用户，我希望能够通过邮箱重置密码，以便重新登录。

### US-4: 验证码保护

作为一个用户，我希望登录和注册时看到验证码，以便保护账户安全。

### US-5: 邮箱验证

作为一个新注册用户，我希望能够验证邮箱，以便激活账户。

### US-6: 登录预览头像

作为一个用户，当我在登录页面输入正确的账号密码后（尚未点击登录），我希望能看到我的头像和用户名，以便确认我登录的是正确的账户，增强安全感和用户体验。

## 功能需求

### 1. 用户登录

- 邮箱/用户名 + 密码登录
- 动态验证码验证
- 记住登录状态（可选）
- 登录失败次数限制（5次后锁定10分钟）
- JWT Token认证

### 2. 用户注册

- 邮箱注册
- 密码强度验证（最少8位，包含字母和数字）
- 动态验证码验证
- 邮箱验证（发送验证邮件）
- 注册成功后自动登录

### 3. 密码找回

- 通过邮箱发送重置链接
- 重置链接有效期（1小时）
- 重置密码表单
- 验证码保护

### 4. 动态验证码

- 图形验证码生成
- 验证码刷新功能
- 验证码有效期（5分钟）
- 验证码存储在Redis中

#### 4.1 验证码加载与显示

**初始加载**：

- 页面加载时自动获取验证码（GET `/api/auth/captcha/`）
- 验证码图片以base64格式返回，直接显示在验证码区域
- 验证码ID存储在组件状态中，用于后续验证

**加载失败处理**：

- 网络错误：显示"Failed to fetch"错误信息和"重试"按钮
- API错误（如500）：显示错误状态码和"重试"按钮
- 点击重试按钮：重新调用获取验证码API

**验证码刷新**：

- 用户点击验证码图片区域：触发刷新（POST `/api/auth/captcha/refresh/`）
- 刷新时会删除旧的验证码ID（如果提供了captcha_id）
- 刷新后自动清空验证码输入框
- 刷新不影响头像预览的显示状态

#### 4.2 验证码输入与实时校验

**输入限制**：

- 验证码输入框限制最大长度为4位
- 自动转换为大写字母
- 只允许输入字母和数字

**实时校验触发条件**：

- 用户输入验证码，输入满4位后立即触发校验
- **重要**：实时校验需要账号密码已填写（因为通过预览API验证）

**校验流程**：

1. 用户输入4位验证码
2. 调用预览API验证验证码（POST `/api/auth/preview/`，包含email、password、captcha_id、captcha_answer）
3. 根据API响应处理：
   - **验证码正确**（API返回200，无INVALID_CAPTCHA错误）：
     - 显示绿色打勾图标
     - 清除所有错误提示
     - 如果账号密码正确，触发头像预览
   - **验证码错误**（API返回400，code=INVALID_CAPTCHA）：
     - 自动刷新验证码图片
     - 清空验证码输入框
     - 显示错误提示"验证码错误，已自动刷新"
     - **重要**：验证码错误不影响头像预览的显示状态

**校验失败处理**：

- 如果只输入验证码，没有输入账号密码，无法进行实时校验（这是设计限制）
- 验证码校验错误不会清除头像预览（如果头像已显示）

#### 4.3 验证码错误处理

**错误场景**：

1. 验证码输入错误：自动刷新验证码，清空输入，显示错误提示
2. 验证码过期：用户提交时后端返回错误，前端显示错误提示并刷新验证码
3. 验证码获取失败：显示错误信息和重试按钮

**错误提示显示**：

- 验证码输入框下方显示红色错误文字
- 错误提示在用户开始重新输入时自动清除（输入长度<4时）
- 验证码错误提示不会影响其他字段的错误提示

### 5. 邮箱验证

- 注册后发送验证邮件
- 验证链接有效期（24小时）
- 验证状态标记
- 重新发送验证邮件

### 6. 登录预览头像（实时验证）

#### 6.1 触发时机与条件

**触发时机**：

1. **密码框失焦**：用户输入密码后，光标离开密码输入框时立即触发
2. **防抖触发**：用户输入邮箱或密码后，停止输入500ms后触发（避免频繁调用API）
3. **验证码更新后**：如果邮箱和密码已填写，验证码ID更新后也会触发预览

**触发条件**（必须同时满足）：

- 邮箱已填写且格式正确
- 密码已填写且长度>=8位
- 验证码ID已存在（验证码组件已加载）

**重要**：预览时验证码答案可以为空（根据PRD，预览时验证码可选）

#### 6.2 预览API调用

**API端点**：POST `/api/auth/preview/`

**请求参数**：

```json
{
  "email": "user@example.com",
  "password": "password123",
  "captcha_id": "uuid-string",
  "captcha_answer": "" // 可选，预览时可以为空
}
```

**API响应**：

- **成功（200）**：
  - `valid: true` + `user`对象：账号密码正确，返回用户信息
  - `valid: false` + `user: null`：账号密码错误
- **验证码错误（400）**：
  - `code: "INVALID_CAPTCHA"`：验证码错误（如果提供了验证码答案）
- **网络错误**：抛出异常

#### 6.3 头像显示逻辑

**成功显示**：

- 当API返回`valid: true`时，在登录表单上方显示用户头像和用户名
- 头像来源：
  - 有头像：显示用户真实头像（`avatar_url`）
  - 无头像：显示基于用户名首字母生成的默认头像（`avatar_letter`）
- 显示动画：淡入动画效果，增强用户体验

**失败处理**：

- 当API返回`valid: false`时，不显示头像区域或清除已显示的头像
- 网络错误：不显示头像，但不清除已显示的头像（避免闪烁）

#### 6.4 头像显示状态管理

**保持显示条件**：
一旦账号密码验证成功（`valid: true`），头像应该一直显示，直到以下情况发生：

- 用户修改了邮箱或密码（导致账号密码验证失败）
- 用户清空了邮箱或密码输入框
- 预览API返回`valid: false`（账号密码错误）

**不受影响的情况**（头像保持显示）：

- **验证码错误**：验证码错误不影响头像显示，头像应保持显示状态
- **验证码刷新**：验证码刷新不影响头像显示，头像应保持显示状态
- **验证码输入**：验证码输入过程不影响头像显示，头像应保持显示状态
- **网络错误**：如果头像已显示，网络错误不应该清除头像（避免闪烁）

**清除条件**：
只有当以下情况发生时，才清除头像显示：

- 账号密码变化导致验证失败（API返回`valid: false`）
- 用户清空了邮箱或密码输入框
- 用户修改了邮箱或密码，新的组合验证失败

#### 6.5 加载状态与错误处理

**加载状态**：

- 调用预览API时显示loading动画
- Loading状态不影响已显示的头像（如果头像已显示）

**错误处理**：

- **验证码错误**：由验证码实时校验处理，不影响头像预览
  - 显示错误提示"验证码错误，已自动刷新"
  - 自动刷新验证码图片
  - 清空验证码输入框
- **网络错误**：不显示错误提示，但记录日志（避免影响用户体验）
- **限流错误（429）**：显示用户友好的提示信息
  - 显示错误提示"请求过于频繁，请稍后再试"
  - 不清除头像（如果头像已显示）
  - 不刷新验证码（避免触发更多API调用）
  - 记录日志用于监控

#### 6.6 安全防护

- **验证码保护**：预验证API需要验证码ID（captcha_id必填），但验证码答案可选（预览时）
- **频率限制**：限制预验证请求频率（同一IP每分钟最多10次）
- **错误信息**：预验证不返回详细错误信息（只返回成功/失败+用户信息），防止暴力枚举

#### 6.7 用户体验优化

- **防抖处理**：避免用户输入时频繁调用API（500ms防抖）
- **加载动画**：头像加载时显示loading动画，增强交互反馈
- **淡入动画**：头像显示时使用淡入动画，提升视觉体验
- **状态保持**：头像一旦显示，不会因为验证码相关操作而消失

## 数据库设计

### User表（已存在，需要扩展）

| 字段名                | 类型         | 说明         | 约束             |
| --------------------- | ------------ | ------------ | ---------------- |
| id                    | UUID         | 主键         | PK, NOT NULL     |
| username              | VARCHAR(150) | 用户名       | UNIQUE, NOT NULL |
| email                 | VARCHAR(255) | 邮箱         | UNIQUE, NOT NULL |
| password              | VARCHAR(255) | 密码哈希     | NOT NULL         |
| is_active             | BOOLEAN      | 是否激活     | DEFAULT TRUE     |
| is_email_verified     | BOOLEAN      | 邮箱是否验证 | DEFAULT FALSE    |
| email_verified_at     | TIMESTAMP    | 邮箱验证时间 | NULL             |
| last_login            | TIMESTAMP    | 最后登录时间 | NULL             |
| failed_login_attempts | INTEGER      | 登录失败次数 | DEFAULT 0        |
| locked_until          | TIMESTAMP    | 锁定到期时间 | NULL             |
| avatar                | VARCHAR(500) | 头像URL      | NULL             |
| display_name          | VARCHAR(100) | 显示名称     | NULL             |
| created_at            | TIMESTAMP    | 创建时间     | DEFAULT NOW()    |
| updated_at            | TIMESTAMP    | 更新时间     | DEFAULT NOW()    |

**索引**：

- idx_email: email (UNIQUE)
- idx_username: username (UNIQUE)
- idx_email_verified: is_email_verified

### EmailVerification表

| 字段名      | 类型         | 说明     | 约束                   |
| ----------- | ------------ | -------- | ---------------------- |
| id          | UUID         | 主键     | PK, NOT NULL           |
| user_id     | UUID         | 用户ID   | FK → User.id, NOT NULL |
| email       | VARCHAR(255) | 验证邮箱 | NOT NULL               |
| token       | VARCHAR(255) | 验证令牌 | UNIQUE, NOT NULL       |
| expires_at  | TIMESTAMP    | 过期时间 | NOT NULL               |
| verified_at | TIMESTAMP    | 验证时间 | NULL                   |
| created_at  | TIMESTAMP    | 创建时间 | DEFAULT NOW()          |

**索引**：

- idx_token: token (UNIQUE)
- idx_user_email: user_id, email

### PasswordReset表

| 字段名     | 类型         | 说明     | 约束                   |
| ---------- | ------------ | -------- | ---------------------- |
| id         | UUID         | 主键     | PK, NOT NULL           |
| user_id    | UUID         | 用户ID   | FK → User.id, NOT NULL |
| token      | VARCHAR(255) | 重置令牌 | UNIQUE, NOT NULL       |
| expires_at | TIMESTAMP    | 过期时间 | NOT NULL               |
| used_at    | TIMESTAMP    | 使用时间 | NULL                   |
| created_at | TIMESTAMP    | 创建时间 | DEFAULT NOW()          |

**索引**：

- idx_token: token (UNIQUE)
- idx_user_id: user_id

### Captcha表（Redis存储，非数据库表）

**Redis Key格式**：

- `captcha:{session_id}`: 验证码答案（5分钟过期）

**数据结构**：

```json
{
  "answer": "A3B7",
  "created_at": "2025-12-03T10:00:00Z",
  "expires_at": "2025-12-03T10:05:00Z"
}
```

## API接口定义

### 0. 登录预验证（获取头像）

**POST** `/api/auth/preview/`

**描述**: 验证账号密码是否正确，正确则返回用户头像和显示名称（不实际登录）

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "captcha_id": "uuid",
  "captcha_answer": "A3B7"
}
```

**成功响应** (200):

```json
{
  "valid": true,
  "user": {
    "display_name": "张三",
    "avatar_url": "https://example.com/avatars/user.jpg",
    "default_avatar": false
  }
}
```

**无头像时响应** (200):

```json
{
  "valid": true,
  "user": {
    "display_name": "张三",
    "avatar_url": null,
    "default_avatar": true,
    "avatar_letter": "张"
  }
}
```

**验证失败响应** (200):

```json
{
  "valid": false,
  "user": null
}
```

**注意**: 为防止用户枚举攻击，无论邮箱是否存在，密码是否正确，都返回200状态码，仅通过`valid`字段区分。

**频率限制**: 同一IP每分钟最多10次请求

### 1. 获取验证码

**GET** `/api/auth/captcha/`

**响应** (200):

```json
{
  "captcha_id": "uuid",
  "captcha_image": "data:image/png;base64,iVBORw0KG...",
  "expires_in": 300
}
```

### 2. 刷新验证码

**POST** `/api/auth/captcha/refresh/`

**请求体**:

```json
{
  "captcha_id": "uuid"
}
```

**响应** (200):

```json
{
  "captcha_id": "new-uuid",
  "captcha_image": "data:image/png;base64,...",
  "expires_in": 300
}
```

### 3. 用户注册

**POST** `/api/auth/register/`

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "captcha_id": "uuid",
  "captcha_answer": "A3B7"
}
```

**成功响应** (201):

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_email_verified": false
  },
  "token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "message": "注册成功，请查收验证邮件"
}
```

**错误响应** (400):

```json
{
  "error": "验证码错误",
  "code": "INVALID_CAPTCHA"
}
```

### 4. 用户登录

**POST** `/api/auth/login/`

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "captcha_id": "uuid",
  "captcha_answer": "A3B7",
  "remember_me": false
}
```

**成功响应** (200):

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user",
    "display_name": "张三",
    "avatar_url": "https://example.com/avatars/user.jpg",
    "is_email_verified": true
  },
  "token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "expires_in": 3600
}
```

**错误响应** (401):

```json
{
  "error": "邮箱或密码错误",
  "code": "INVALID_CREDENTIALS",
  "failed_attempts": 3,
  "locked_until": null
}
```

**账户锁定响应** (423):

```json
{
  "error": "账户已锁定，请10分钟后重试",
  "code": "ACCOUNT_LOCKED",
  "locked_until": "2025-12-03T10:10:00Z"
}
```

### 5. 发送邮箱验证邮件

**POST** `/api/auth/email/verify/send/`

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "email": "user@example.com"
}
```

**响应** (200):

```json
{
  "message": "验证邮件已发送，请查收"
}
```

### 6. 验证邮箱

**GET** `/api/auth/email/verify/{token}/`

**响应** (200):

```json
{
  "message": "邮箱验证成功",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_email_verified": true
  }
}
```

### 7. 发送密码重置邮件

**POST** `/api/auth/password/reset/send/`

**请求体**:

```json
{
  "email": "user@example.com",
  "captcha_id": "uuid",
  "captcha_answer": "A3B7"
}
```

**响应** (200):

```json
{
  "message": "密码重置邮件已发送，请查收"
}
```

### 8. 重置密码

**POST** `/api/auth/password/reset/`

**请求体**:

```json
{
  "token": "reset-token",
  "password": "NewSecurePass123",
  "password_confirm": "NewSecurePass123"
}
```

**响应** (200):

```json
{
  "message": "密码重置成功，请使用新密码登录"
}
```

### 9. 刷新Token

**POST** `/api/auth/token/refresh/`

**请求体**:

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

**响应** (200):

```json
{
  "token": "new-jwt-access-token",
  "expires_in": 3600
}
```

### 10. 用户登出

**POST** `/api/auth/logout/`

**请求头**:

```
Authorization: Bearer {token}
```

**响应** (200):

```json
{
  "message": "登出成功"
}
```

## 前端组件设计

### 页面结构

```
LoginView.vue (登录主页面)
├── LoginForm.vue (登录表单)
│   ├── FloatingInput.vue (悬浮式输入框组件)
│   ├── Captcha.vue (验证码组件)
│   ├── RememberMe.vue (记住我复选框)
│   └── UserPreview.vue (用户预览组件 - 显示头像和用户名)
├── RegisterForm.vue (注册表单)
│   ├── FloatingInput.vue
│   ├── PasswordStrength.vue (密码强度指示器)
│   └── Captcha.vue
└── PasswordResetForm.vue (密码重置表单)
    ├── FloatingInput.vue
    └── Captcha.vue
```

### 组件层次

**LoginView.vue** (主容器)

- 背景设计（渐变/图片，非AI通用配色）
- 响应式布局（桌面/移动端）
- 表单切换（登录/注册/密码找回）

**FloatingInput.vue** (悬浮式输入框)

- 输入时标签上浮动画
- 错误状态显示
- 图标支持（邮箱、密码、验证码）

**Captcha.vue** (验证码组件)

- 验证码图片显示
- 刷新按钮
- 输入框
- 加载状态

**PasswordStrength.vue** (密码强度指示器)

- 实时强度检测
- 视觉反馈（颜色条）
- 强度提示文字

**UserPreview.vue** (用户预览组件)

- 圆形头像显示（有头像显示真实头像，无头像显示首字母）
- 用户显示名称
- 加载中状态（骨架屏/spinner）
- 验证失败状态（隐藏或显示占位）
- 淡入动画效果
- 位置：登录表单上方居中

### 状态管理

**Pinia Store: `stores/auth.ts`**

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  captcha: {
    id: string | null;
    image: string | null;
  };
  // 登录预览状态
  preview: {
    isLoading: boolean;
    isValid: boolean | null; // null=未验证, true=验证通过, false=验证失败
    displayName: string | null;
    avatarUrl: string | null;
    avatarLetter: string | null; // 默认头像显示的首字母
  };
}

interface AuthActions {
  login(email: string, password: string, captcha: string): Promise<void>;
  register(data: RegisterData): Promise<void>;
  logout(): void;
  refreshToken(): Promise<void>;
  sendPasswordReset(email: string, captcha: string): Promise<void>;
  resetPassword(token: string, password: string): Promise<void>;
  sendEmailVerification(): Promise<void>;
  verifyEmail(token: string): Promise<void>;
  fetchCaptcha(): Promise<void>;
  refreshCaptcha(): Promise<void>;
  // 登录预验证（获取头像）
  previewLogin(
    email: string,
    password: string,
    captchaId: string,
    captchaAnswer: string,
  ): Promise<void>;
  clearPreview(): void;
}
```

### 交互流程

#### 登录流程（详细交互逻辑）

**步骤1：页面加载**

- 用户访问 `/login`
- 自动获取验证码（GET `/api/auth/captcha/`）
- 验证码图片显示在验证码区域
- 验证码ID存储在组件状态中

**步骤2：用户输入邮箱**

- 用户输入邮箱地址
- 实时验证邮箱格式（使用EMAIL_REGEX）
- 格式正确：显示绿色打勾图标
- 格式错误：显示错误提示"请输入有效的邮箱地址"

**步骤3：用户输入密码**

- 用户输入密码
- 实时验证密码长度（>=8位）
- 长度正确：显示绿色打勾图标
- 长度不足：显示错误提示"密码长度至少为8位"
- **密码框失焦**：如果邮箱和密码都已填写且格式正确，触发预览API

**步骤4：头像预览触发（预验证）**

- **触发条件**：
  - 邮箱已填写且格式正确
  - 密码已填写且长度>=8位
  - 验证码ID已存在（验证码组件已加载）
- **触发时机**：
  - 密码框失焦时立即触发
  - 停止输入500ms后触发（防抖）
  - 验证码ID更新后触发（如果邮箱和密码已填写）
- **API调用**：POST `/api/auth/preview/`
  - 请求参数：`{email, password, captcha_id, captcha_answer: ""}`（验证码答案可选）
  - 成功（valid: true）：显示用户头像和用户名
  - 失败（valid: false）：不显示头像或清除已显示的头像
  - 验证码错误（400）：由验证码实时校验处理，不影响头像预览

**步骤5：用户输入验证码**

- 用户输入验证码（4位）
- **实时校验**（输入满4位后立即触发）：
  - 调用预览API验证验证码（需要账号密码已填写）
  - 验证码正确：显示绿色打勾图标，清除错误提示
  - 验证码错误：自动刷新验证码，清空输入框，显示错误提示"验证码错误，已自动刷新"
  - **重要**：验证码校验不影响头像预览的显示状态

**步骤6：用户点击登录按钮**

- **前端验证**（必须全部通过）：
  - 邮箱格式正确
  - 密码长度>=8位
  - 验证码ID已存在
  - 验证码答案已输入（4位）
- **验证失败**：显示对应字段的错误提示，不提交
- **验证通过**：调用登录API

**步骤7：登录API调用**

- API调用：POST `/api/auth/login/`
- 请求参数：`{email, password, captcha_id, captcha_answer}`
- **成功（200）**：
  - 保存token到localStorage
  - 更新auth store状态
  - 跳转到首页（`router.push('/')`）
- **失败处理**：
  - 验证码错误（400, code=INVALID_CAPTCHA）：
    - 显示错误提示"验证码错误，请重新输入"
    - 自动刷新验证码
    - **不清除头像预览**（如果头像已显示）
  - 账号密码错误（401, code=INVALID_CREDENTIALS）：
    - 显示错误提示"邮箱或密码错误"（在密码输入框下方）
    - **清除头像预览**（因为账号密码错误）
  - 其他错误：显示错误提示在邮箱输入框下方

**步骤8：错误提示显示规则**

- 邮箱错误：显示在邮箱输入框下方（红色文字）
- 密码错误：显示在密码输入框下方（红色文字）
- 验证码错误：显示在验证码输入框下方（红色文字）
- 错误提示在用户开始重新输入时自动清除（对应字段）

#### 注册流程（详细交互逻辑）

**步骤1：切换到注册表单**

- 用户点击"注册"链接或切换到注册表单
- 自动获取验证码（GET `/api/auth/captcha/`）
- 验证码图片显示在验证码区域（Captcha组件）

**步骤2：用户填写邮箱**

- 用户输入邮箱地址
- 实时验证邮箱格式
- 格式正确：显示绿色打勾图标
- 格式错误：显示错误提示

**步骤3：用户输入密码**

- 用户输入密码
- 实时密码强度检测（显示密码强度指示器）
- 密码强度要求：最少8位，包含字母和数字
- 强度不足：显示错误提示

**步骤4：用户输入确认密码**

- 用户输入确认密码
- 实时验证密码是否匹配
- 不匹配：显示错误提示"密码和确认密码不一致"

**步骤5：用户输入验证码**

- 用户在Captcha组件的输入框中输入验证码（4位）
- **注意**：注册页面只有一个验证码输入框（在Captcha组件内部）
- 验证码输入通过`@captcha-update`事件传递给RegisterForm
- 输入满4位后自动验证（如果邮箱和密码已填写）

**步骤6：用户点击注册按钮**

- **前端验证**（必须全部通过）：
  - 邮箱格式正确
  - 密码强度符合要求
  - 确认密码匹配
  - 验证码ID已存在
  - 验证码答案已输入（4位）
- **验证失败**：显示对应字段的错误提示，不提交
- **验证通过**：调用注册API

**步骤7：注册API调用**

- API调用：POST `/api/auth/register/`
- 请求参数：`{email, password, password_confirm, captcha_id, captcha_answer}`
- **成功（201）**：
  - 保存token到localStorage
  - 更新auth store状态
  - 显示邮箱验证提示界面
  - 提示用户查收验证邮件
- **失败处理**：
  - 验证码错误（400, code=INVALID_CAPTCHA）：
    - 显示错误提示"验证码错误"
    - 自动刷新验证码
    - 清空验证码输入框
  - 邮箱已存在（400, code=EMAIL_EXISTS）：
    - 显示错误提示"该邮箱已被注册"
  - 密码强度不足（400, code=WEAK_PASSWORD）：
    - 显示错误提示"密码必须包含字母和数字"
  - 其他错误：显示错误提示

**步骤8：邮箱验证提示**

- 注册成功后显示邮箱验证提示界面
- 提示用户查收验证邮件（包括垃圾邮件文件夹）
- 提供"重新发送验证邮件"按钮
- 提供"返回首页"按钮

#### 密码找回流程

1. 切换到密码找回表单
2. 获取验证码
3. 用户填写邮箱、验证码
4. 点击"发送重置邮件"
5. 调用API: `POST /api/auth/password/reset/send/`
6. 成功：提示查收邮件
7. 用户点击邮件中的重置链接
8. 跳转到重置密码页面
9. 填写新密码
10. 调用API: `POST /api/auth/password/reset/`
11. 成功：提示使用新密码登录

## 测试策略

### 后端测试

#### 单元测试

**`backend/tests/unit/test_auth_views.py`**

- 测试登录视图逻辑
- 测试注册视图逻辑
- 测试密码重置视图逻辑
- 测试Token生成和验证
- 测试登录失败次数限制
- 测试账户锁定机制

**`backend/tests/unit/test_captcha.py`**

- 测试验证码生成
- 测试验证码验证
- 测试验证码过期
- 测试Redis存储

#### 集成测试

**`backend/tests/integration/test_auth_api.py`**

- 测试完整的登录流程
- 测试完整的注册流程
- 测试Token刷新
- 测试登出功能
- 测试并发登录

**`backend/tests/integration/test_password_reset.py`**

- 测试密码重置邮件发送
- 测试密码重置链接验证
- 测试密码重置流程
- 测试重置链接过期

### 前端测试

#### 组件测试

**`frontend/src/components/auth/__tests__/LoginForm.spec.ts`**

- 测试表单渲染
- 测试表单验证
- 测试提交逻辑
- 测试错误处理

**`frontend/src/components/auth/__tests__/Captcha.spec.ts`**

- 测试验证码显示
- 测试刷新功能
- 测试输入验证

#### E2E测试

**`e2e/tests/auth/login.spec.ts`**

- 测试完整登录流程
- 测试登录失败场景
- 测试账户锁定场景
- 测试登录后跳转

**`e2e/tests/auth/register.spec.ts`**

- 测试完整注册流程
- 测试注册验证
- 测试注册后自动登录

**`e2e/tests/auth/password-reset.spec.ts`**

- 测试密码重置邮件发送
- 测试密码重置链接点击
- 测试密码重置表单提交

**E2E测试错误监听机制（重要）**

**问题背景**：

- Playwright默认不会因控制台错误而失败测试
- 测试只检查UI状态，不检查JavaScript错误
- 运行时错误（如`ReferenceError`）可能被Promise catch捕获，但测试应该验证是否有未处理的错误

**解决方案**：
所有E2E测试必须使用 `ConsoleErrorListener` 来捕获控制台错误和未处理的Promise rejection：

```typescript
import { ConsoleErrorListener } from "../_helpers/console-error-listener";

test.describe("功能测试", () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    // ... 其他初始化代码（如goto页面）
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误（如果有错误，测试会失败）
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });
});
```

**错误监听器功能**：

- **监听控制台错误**：捕获所有 `console.error` 输出
- **监听页面错误**：捕获 `pageerror` 事件（包括未处理的异常）
- **监听未处理的Promise rejection**：捕获 `unhandledrejection` 事件
- **测试失败机制**：在测试结束时验证是否有错误，如果有错误则测试失败
- **智能过滤**：自动过滤第三方脚本错误、浏览器警告、预期网络错误

**为什么需要错误监听**：

1. **发现隐藏的bug**：JavaScript错误可能不影响UI显示，但会导致功能异常
2. **提高测试质量**：确保测试不仅验证UI，还验证代码质量
3. **早期发现问题**：在开发阶段就能发现运行时错误，而不是等到用户报告

**智能错误过滤（解决三大挑战）**：

**挑战1：第三方脚本的噪音**

- **问题**：Google Analytics、Sentry、广告脚本等可能产生错误，但这些错误与业务代码无关
- **解决方案**：自动识别并过滤第三方脚本错误（通过域名/URL模式匹配）
- **配置**：

```typescript
// 默认已启用第三方脚本错误过滤
errorListener = new ConsoleErrorListener(page, {
  ignoreThirdPartyErrors: true, // 默认true
});
```

**挑战2：浏览器兼容性警告**

- **问题**：浏览器经常输出 [Deprecation] 警告或 Resource failed to load 错误，这些通常不影响功能
- **解决方案**：自动识别并过滤浏览器兼容性警告
- **配置**：

```typescript
errorListener = new ConsoleErrorListener(page, {
  ignoreBrowserWarnings: true, // 默认true
});
```

**挑战3："预期的"错误**

- **问题**：测试用例可能故意触发错误（如测试"输入错误密码"功能，可能产生401错误日志）
- **解决方案**：自动过滤网络错误（400/401/404等），支持自定义过滤规则
- **配置**：

```typescript
// 方式1：使用默认配置（自动过滤网络错误）
errorListener = new ConsoleErrorListener(page, {
  ignoreNetworkErrors: true, // 默认true
});

// 方式2：自定义过滤规则
errorListener = new ConsoleErrorListener(page, {
  ignorePatterns: [/特定的错误消息/i, /另一个错误模式/i],
  // 或者使用函数过滤
  ignoreBySource: (error) => {
    // 自定义过滤逻辑
    return error.message.includes("特定错误");
  },
});

// 方式3：在断言时临时覆盖配置
errorListener.assertNoErrors({
  ignoreNetworkErrors: false, // 临时不忽略网络错误
});
```

**高级配置示例**：

```typescript
import {
  ConsoleErrorListener,
  ErrorFilterConfig,
} from "../_helpers/console-error-listener";

test.describe("功能测试", () => {
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    // 自定义过滤配置
    const filterConfig: Partial<ErrorFilterConfig> = {
      ignoreNetworkErrors: true, // 忽略网络错误（默认true）
      ignoreBrowserWarnings: true, // 忽略浏览器警告（默认true）
      ignoreThirdPartyErrors: true, // 忽略第三方脚本错误（默认true）
      ignorePatterns: [
        /特定的错误消息/i, // 自定义忽略模式
      ],
      allowedPatterns: [
        /必须捕获的错误/i, // 白名单：即使匹配忽略规则，也要捕获
      ],
      ignoreBySource: (error) => {
        // 自定义过滤函数
        if (error.message.includes("特定条件")) {
          return true; // 忽略此错误
        }
        return false;
      },
    };

    errorListener = new ConsoleErrorListener(page, filterConfig);
    errorListener.startListening();
  });

  test.afterEach(async () => {
    // 获取错误统计（用于调试）
    const stats = errorListener.getErrorStats();
    console.log("错误统计:", stats);
    // 输出示例：
    // {
    //   total: 2,
    //   byType: { console: 1, pageerror: 1 },
    //   bySource: { application: 2 }
    // }

    // 验证是否有错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });
});
```

**错误来源分类**：

- `application`：业务代码错误（必须修复）
- `third-party`：第三方脚本错误（默认忽略）
- `browser`：浏览器兼容性警告（默认忽略）
- `network`：网络请求错误（默认忽略，测试中可能故意触发）

**实施要求**：

- ✅ 所有新的E2E测试必须使用 `ConsoleErrorListener`
- ✅ 现有测试逐步迁移到使用错误监听器
- ✅ CI/CD中如果测试有控制台错误，应该失败
- ✅ 根据项目实际情况配置错误过滤规则

**已应用错误监听器的测试文件**（共11个文件）：

- ✅ `test-login-preview.spec.ts` - 登录预览功能测试（5个测试）
- ✅ `test-captcha-realtime-validation.spec.ts` - 验证码实时校验功能测试（3个测试）
- ✅ `test-captcha-refresh.spec.ts` - 验证码刷新功能测试（3个测试）
- ✅ `test-email-verification.spec.ts` - 邮箱验证功能测试
- ✅ `test-password-reset.spec.ts` - 密码找回功能测试
- ✅ `test-register-integration.spec.ts` - 注册流程集成测试
- ✅ `test-register-button.spec.ts` - 注册页面按钮验证测试
- ✅ `test-register-form-instances.spec.ts` - 注册表单实例验证测试
- ✅ `test-captcha-lifecycle.spec.ts` - 验证码生命周期测试
- ✅ `test-captcha-data-flow.spec.ts` - 验证码数据流完整性测试
- ✅ `test-ui-design.spec.ts` - UI设计规范测试
- ✅ `test-ui-animations.spec.ts` - UI动画效果测试

## 技术实现细节

### 后端技术栈

- **Django REST Framework**: API开发
- **djangorestframework-simplejwt**: JWT认证
- **django-cors-headers**: CORS处理
- **Pillow**: 验证码图片生成
- **Redis**: 验证码存储和会话管理
- **Celery**: 异步邮件发送
- **django-email-utils**: 邮件发送工具

### 前端技术栈

- **Vue 3 Composition API**: 组件开发
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Axios**: HTTP客户端
- **VeeValidate**: 表单验证
- **GSAP / Vue Transition**: 动画效果
- **Tailwind CSS / 自定义CSS**: 样式设计

### 验证码实现

**生成算法**:

- 使用Pillow生成4位数字+字母混合验证码
- 添加干扰线和噪点
- Base64编码返回

**存储方案**:

- Redis存储，Key: `captcha:{session_id}`
- 5分钟过期
- 验证后立即删除

### 密码安全

- **哈希算法**: Django内置PBKDF2（自动加盐）
- **密码强度**: 最少8位，包含字母和数字
- **重置链接**: UUID token，1小时有效期
- **登录保护**: 5次失败后锁定10分钟

### 邮件发送

- **异步任务**: 使用Celery异步发送
- **邮件模板**: HTML模板，支持品牌样式
- **重试机制**: 失败后自动重试3次
- **发送队列**: 使用Redis作为消息队列

### UI设计规范

## Figma设计规范（权威标准）

**Figma设计链接**: https://www.figma.com/design/n7oYkASiqv2vgBpix0X9mi/Login-register-V1.0?node-id=0-1

**⚠️ 重要**: 以下设计规范来自Figma设计稿，是实现的唯一标准。所有实现必须严格按照这些规范执行。

### 整体布局

**主容器 (AuthCard)**:

- 宽度: 1152px
- 高度: 721.333px
- 背景: `rgba(255,255,255,0.75)` (白色75%透明度)
- 边框: `0.667px solid rgba(255,255,255,0.5)`
- 圆角: `16px`
- 阴影: `0px 8px 32px 0px rgba(249,115,22,0.1), 0px 0px 0px 1px rgba(249,115,22,0.1)`
- 内阴影: `inset 0px 0px 60px 0px rgba(255,255,255,0.3)`

**左右分栏布局**:

- 左侧面板: 460.26px (品牌展示区)
- 右侧面板: 690.406px (登录表单区)
- 分隔线: `2px solid rgba(255,237,212,1)` (右侧边框)

### 颜色规范

**主色调**:

- 橙色主色: `#f97316` / `#ff6900` / `#ff8904`
- 橙色渐变: `linear-gradient(135deg, rgba(255, 137, 4, 1) 0%, rgba(253, 199, 0, 1) 100%)`
- 绿色: `#22c55e` / `rgba(5, 223, 114, 1)`
- 绿色渐变: `linear-gradient(135deg, rgba(5, 223, 114, 1) 0%, rgba(0, 212, 146, 1) 100%)`
- 蓝色: `rgba(81, 162, 255, 1)` / `rgba(0, 211, 242, 1)`
- 蓝色渐变: `linear-gradient(135deg, rgba(81, 162, 255, 1) 0%, rgba(0, 184, 219, 1) 100%)`

**文字颜色**:

- 主标题: `#1e2939` (深灰黑)
- 副标题/正文: `#4a5565` (中灰)
- 占位符: `#99a1af` (浅灰)
- 标签文字: `#364153` (深灰)
- 链接/强调: `#ff6900` (橙色)

**背景颜色**:

- 输入框背景: `rgba(255,255,255,0.6)` (白色60%透明度)
- 验证码背景: `linear-gradient(158.2deg, rgba(255, 237, 213, 1) 0%, rgba(254, 243, 199, 1) 100%)`
- Demo提示框: `linear-gradient(to right, #fff7ed, #fefce8)`
- 功能卡片背景:
  - English Learning: `linear-gradient(to right, rgba(255,247,237,0.5), #fff7ed)`
  - Coding Practice: `linear-gradient(to right, rgba(240,253,244,0.5), #f0fdf4)`
  - Career Growth: `linear-gradient(to right, rgba(239,246,255,0.5), #eff6ff)`

**边框颜色**:

- 输入框边框: `2px solid rgba(249,115,22,0.15)` (橙色15%透明度)
- 验证码边框: `2px solid #ffd6a7` (浅橙色)
- 装饰边框: `rgba(255,137,4,0.4)` (橙色40%透明度)

### 尺寸规范

**输入框**:

- 高度: 60px
- 圆角: 14px
- 内边距: `16px 48px` (上下16px, 左右48px，左侧为图标预留空间)
- 图标尺寸: 20px × 20px
- 图标位置: 左侧16px，垂直居中

**验证码区域**:

- 验证码显示框: 160px × 64px
- 验证码输入框: 402.406px × 64px
- 验证码文字: 30px，粗体
- 刷新按钮: 24px × 24px

**标签**:

- 高度: 20px
- 字体大小: 14px，粗体
- 字间距: 0.35px
- 颜色: `#364153`

**按钮**:

- 登录按钮: 需要根据设计确定（当前代码中未明确）

### 字体规范

**字体族**: Arial (Bold/Regular)

**字体大小**:

- 主标题 (Welcome Back): 20px, 粗体, 行高30px, 字间距0.5px
- 副标题: 16px, 常规, 行高24px
- 标签: 14px, 粗体, 行高20px, 字间距0.35px
- 占位符: 16px, 常规
- 验证码文字: 30px, 粗体, 行高36px
- 验证码输入: 20px, 粗体, 字间距2px, 居中

### 间距规范

**容器内边距**:

- 右侧面板: `56px` (左右)
- 左侧面板: `48px` (左右上下)

**元素间距**:

- 输入框组间距: 24px
- 标签与输入框间距: 12px
- 功能卡片间距: 16px

### 左侧品牌展示区

**Logo区域**:

- Logo尺寸: 56.179px × 56.179px
- Logo背景: 橙色渐变，圆角14px
- 标题: "Learning Hub" - 16px, 粗体, `#1e2939`
- 副标题: "Grow Every Day" - 14px, 常规, `#ff6900`

**欢迎文字**:

- 字体: 16px, 常规, 行高26px
- 颜色: `#4a5565`
- 内容: "Welcome to your personal learning space for English, Coding, and Career Growth"

**中央插图**:

- 尺寸: 256px × 256px
- 包含: 圆形装饰线条、渐变方块（橙色/绿色/蓝色）、小圆点装饰
- 位置: 居中

**功能卡片** (3个):

- 高度: 60px
- 圆角: 14px
- 图标: 36px × 36px，渐变背景
- 标题: 14px, 粗体, `#1e2939`
- 描述: 12px, 常规, `#4a5565`

### 右侧登录表单区

**标题区域**:

- "Welcome Back" - 20px, 粗体, `#1e2939`
- "Continue your learning journey" - 16px, 常规, `#4a5565`
- 间距: 8px

**输入框组**:

- USERNAME: 标签 + 输入框 (92px总高度)
- PASSWORD: 标签 + 输入框 (92px总高度)
- SECURITY CODE: 标签 + 验证码区域 (96px总高度)

**Demo账户提示框**:

- 高度: 72px
- 圆角: 14px
- 边框: `2px solid #ffd6a7`
- 背景: 橙色到黄色渐变
- 图标: 36px × 36px，橙色背景 `#ff8904`
- 文字: 14px, `#ca3500`

**注册链接**:

- 文字: "Don't have an account?" - 14px, `#4a5565`
- 链接: "Sign up now →" - 14px, 粗体, `#ff6900`

### 装饰元素

**顶部渐变条**:

- 高度: 4px
- 渐变: `linear-gradient(90deg, rgba(249, 115, 22, 0.5) 0%, rgba(234, 179, 8, 0.5) 33.333%, rgba(34, 197, 94, 0.5) 66.667%, rgba(249, 115, 22, 0.5) 100%)`

**四角装饰边框**:

- 尺寸: 80px × 80px
- 边框: 2px, 40%透明度
- 颜色: 橙色/黄色/绿色

### 响应式断点

**桌面端** (当前设计):

- 最小宽度: 1152px
- 左右分栏布局

**平板端** (需要设计):

- 768px - 1024px
- 可能需要调整布局

**移动端** (需要设计):

- < 768px
- 单列布局，可能需要隐藏左侧面板

### 动画效果

**输入框交互**:

- Focus状态: 边框颜色可能需要变化（设计稿中未明确，需确认）
- 内阴影效果: `inset 0px 0px 20px 0px rgba(255,255,255,0.5)`

**验证码刷新**:

- 刷新按钮有旋转动画（162.36deg）

### 实现注意事项

1. **精确还原**: 所有尺寸、颜色、间距必须严格按照上述规范实现
2. **透明度处理**: 使用`rgba`或CSS变量确保透明度准确
3. **渐变实现**: 使用CSS `linear-gradient`精确还原渐变角度和颜色
4. **字体回退**: Arial不可用时使用系统sans-serif字体
5. **响应式适配**: 桌面端严格按照设计，移动端需要合理适配

**配色方案**（避免AI通用配色）:

- 主色调: 深蓝 (#1a237e) + 金色 (#ffd700)
- 背景: 渐变 (#667eea → #764ba2)
- 输入框: 白色背景，深色边框
- 按钮: 主色调渐变，悬停效果
- 错误: 红色 (#ef4444)
- 成功: 绿色 (#10b981)

**悬浮式输入框**:

- 标签默认在输入框内
- 输入时标签上浮并缩小
- 使用CSS transform和transition
- 支持图标和错误提示

**响应式设计**:

- 移动端: 单列布局，全屏表单
- 桌面端: 左右分栏（表单+品牌展示）
- 断点: 768px, 1024px, 1440px

## 产品逻辑

### 注册流程逻辑

1. **邮箱验证**

   - 注册时发送验证邮件
   - 用户可先登录，但部分功能受限
   - 24小时内完成验证

2. **密码策略**

   - 最少8位
   - 必须包含字母和数字
   - 实时强度提示
   - 不允许使用常见弱密码

3. **验证码策略**
   - 每次登录/注册都需要验证码
   - 验证码5分钟有效
   - 验证失败后自动刷新
   - 支持手动刷新

### 登录安全逻辑

1. **失败次数限制**

   - 5次失败后锁定账户
   - 锁定时间10分钟
   - 锁定期间显示倒计时
   - 锁定期间验证码仍然需要

2. **Token管理**

   - Access Token: 1小时有效期
   - Refresh Token: 7天有效期
   - Token存储在HTTP-only Cookie（可选）
   - 支持"记住我"功能（延长Refresh Token有效期）

3. **会话管理**
   - 支持多设备登录
   - 登出时清除所有Token
   - 支持强制下线其他设备

### 密码找回逻辑

1. **邮件发送**

   - 验证邮箱是否存在
   - 发送重置链接（包含token）
   - 链接1小时有效
   - 同一邮箱1小时内只能发送一次

2. **重置流程**
   - 验证token有效性
   - 验证token未使用
   - 更新密码后使token失效
   - 发送密码变更通知邮件

### 邮箱验证逻辑

1. **验证时机**

   - 注册时自动发送
   - 用户可手动重新发送
   - 重新发送间隔5分钟

2. **验证状态**
   - 未验证: 部分功能受限
   - 已验证: 全部功能可用
   - 验证后更新用户状态

## 验收标准

### 功能验收

- [ ] 用户可以成功注册账户
- [ ] 用户可以成功登录
- [ ] 用户可以找回密码
- [ ] 用户可以验证邮箱
- [ ] 验证码可以正常显示和刷新
- [ ] 登录失败5次后账户被锁定
- [ ] 密码强度验证正常工作
- [ ] 所有API接口返回正确的JSON格式
- [ ] **登录预览头像**：输入正确账号密码后显示用户头像和名称
- [ ] **默认头像**：无头像用户显示首字母默认头像
- [ ] **预验证安全**：预验证API受验证码保护，频率限制正常工作

### UI/UX验收

- [ ] 悬浮式输入框动画流畅
- [ ] 配色方案符合品牌要求（非AI通用配色）
- [ ] 响应式设计在移动端和桌面端都正常
- [ ] 错误提示清晰明确
- [ ] 加载状态有视觉反馈
- [ ] 表单验证实时提示
- [ ] **头像预览**：头像显示位置合理，淡入动画流畅
- [ ] **默认头像**：首字母头像样式美观，与整体设计协调

### 安全验收

- [ ] 密码正确哈希存储
- [ ] JWT Token安全生成和验证
- [ ] 验证码正确验证和过期
- [ ] 登录失败次数限制生效
- [ ] 密码重置链接安全有效
- [ ] 邮箱验证链接安全有效

### 测试验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有E2E测试通过
- [ ] 代码覆盖率 >= 80%

## 实施优先级

### Phase 1 (MVP - 2周)

- 数据库表创建和迁移
- 基础API实现（登录、注册）
- 验证码生成和验证
- 基础前端表单（无动画）

### Phase 2 (增强 - 1周)

- 密码找回功能
- 邮箱验证功能
- 悬浮式输入框动画
- 密码强度指示器
- **登录预验证API实现**
- **头像预览组件开发**
- **默认头像生成逻辑**

### Phase 3 (优化 - 1周)

- UI美化（品牌配色）
- 响应式优化
- 性能优化
- 安全加固

## 风险与缓解

### 技术风险

1. **验证码被破解**

   - 缓解: 使用复杂验证码，添加干扰
   - 缓解: 限制验证码尝试次数

2. **邮件发送失败**

   - 缓解: 使用异步任务，添加重试机制
   - 缓解: 提供备用邮件服务

3. **Token泄露**

   - 缓解: 使用HTTP-only Cookie
   - 缓解: 设置合理的过期时间

4. **预验证API被滥用（用户枚举攻击）**
   - 缓解: 必须携带有效验证码才能调用
   - 缓解: 频率限制（每IP每分钟10次）
   - 缓解: 无论成功失败都返回200，仅通过valid字段区分
   - 缓解: 不返回详细错误信息

### 产品风险

1. **用户体验不佳**

   - 缓解: 充分的用户测试
   - 缓解: 收集用户反馈并迭代

2. **安全漏洞**
   - 缓解: 代码审查
   - 缓解: 安全测试

## 测试用例

### 单元测试

1. **用户模型测试**

   - 测试用户创建和密码哈希
   - 测试邮箱验证逻辑
   - 测试用户状态管理

2. **认证视图测试**

   - 测试登录API端点
   - 测试注册API端点
   - 测试密码重置API端点
   - 测试预验证API端点

3. **预验证功能测试**
   - 测试正确账号密码返回头像和用户名
   - 测试错误账号密码返回valid=false
   - 测试无头像用户返回首字母
   - 测试频率限制（超过10次/分钟被拒绝）
   - 测试无验证码时请求被拒绝

### 集成测试

1. **登录流程测试**

   - 测试完整的登录流程
   - 测试JWT token生成和验证
   - 测试图形验证码验证

2. **密码重置流程测试**
   - 测试密码重置邮件发送
   - 测试密码重置token验证
   - 测试密码更新

### E2E测试

1. **登录页面测试**

   - 测试登录表单提交
   - 测试验证码刷新
   - 测试错误提示显示

2. **注册页面测试**

   - 测试注册表单提交
   - 测试邮箱验证
   - 测试密码强度检查

3. **密码重置测试**

   - 测试密码重置请求
   - 测试密码重置确认
   - 测试密码重置成功跳转

4. **登录预览头像测试**
   - 测试输入正确账号密码后头像显示
   - 测试头像加载动画
   - 测试无头像用户显示默认首字母头像
   - 测试输入错误账号密码头像不显示
   - 测试修改密码后头像消失
   - 测试预验证后点击登录的完整流程

## 附录

### 参考资源

- Django REST Framework文档
- Vue 3官方文档
- JWT认证最佳实践
- 验证码生成算法

### 相关文档

- API契约: `docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml`
- UI设计稿: `docs/00_product/requirements/REQ-2025-003-user-login/attachments/ui-design.png`
