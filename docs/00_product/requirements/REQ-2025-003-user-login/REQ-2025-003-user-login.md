---
req_id: REQ-2025-003-user-login
title: Bravo网站登录页面设计
status: approved
priority: high
type: feature
created_at: 2025-12-03T10:00:00Z
updated_at: 2025-12-03T10:00:00Z
author: human
refined_by: cursor
test_files:
  - backend/tests/unit/test_auth_views.py
  - backend/tests/unit/test_captcha.py
  - backend/tests/integration/test_auth_api.py
  - backend/tests/integration/test_password_reset.py
  - e2e/tests/auth/login.spec.ts
  - e2e/tests/auth/register.spec.ts
  - e2e/tests/auth/password-reset.spec.ts
implementation_files:
  - backend/apps/users/models.py
  - backend/apps/users/views.py
  - backend/apps/users/serializers.py
  - backend/apps/users/utils.py
  - frontend/src/views/Login.vue
  - frontend/src/components/auth/LoginForm.vue
  - frontend/src/components/auth/RegisterForm.vue
  - frontend/src/components/auth/PasswordResetForm.vue
  - frontend/src/components/auth/Captcha.vue
  - frontend/src/stores/auth.ts
  - frontend/src/api/auth.ts
api_contract: docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml
deletable: false
---

# REQ-2025-003-user-login: Bravo网站登录页面设计

## 原始需求

登录网址页面设计，提供登录注册功能，以及动态验证码，密码找回，验证码刷新等等，现代风格UI设计，悬浮式输入框，不要使用通用的AI配色方案。

## 功能概述

设计并实现一个现代化的用户认证系统，包括登录、注册、密码找回、邮箱验证、动态验证码等功能。采用现代UI设计风格，使用悬浮式输入框，提供流畅的用户体验。

## 业务背景

用户认证是网站的核心功能，需要提供安全、便捷、美观的登录体验。现代用户对UI设计要求较高，需要避免千篇一律的AI生成配色方案，打造独特的品牌视觉风格。

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

### 5. 邮箱验证

- 注册后发送验证邮件
- 验证链接有效期（24小时）
- 验证状态标记
- 重新发送验证邮件

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
│   └── RememberMe.vue (记住我复选框)
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
}
```

### 交互流程

#### 登录流程

1. 用户访问 `/login`
2. 自动获取验证码
3. 用户填写邮箱、密码、验证码
4. 点击"登录"按钮
5. 前端验证（格式、非空）
6. 调用API: `POST /api/auth/login/`
7. 成功：保存token，跳转首页
8. 失败：显示错误，刷新验证码

#### 注册流程

1. 切换到注册表单
2. 获取验证码
3. 用户填写邮箱、密码、确认密码、验证码
4. 实时密码强度检测
5. 点击"注册"按钮
6. 调用API: `POST /api/auth/register/`
7. 成功：自动登录，提示验证邮箱
8. 失败：显示错误，刷新验证码

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

### UI/UX验收

- [ ] 悬浮式输入框动画流畅
- [ ] 配色方案符合品牌要求（非AI通用配色）
- [ ] 响应式设计在移动端和桌面端都正常
- [ ] 错误提示清晰明确
- [ ] 加载状态有视觉反馈
- [ ] 表单验证实时提示

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

## 附录

### 参考资源

- Django REST Framework文档
- Vue 3官方文档
- JWT认证最佳实践
- 验证码生成算法

### 相关文档

- API契约: `docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml`
- UI设计稿: `docs/00_product/requirements/REQ-2025-003-user-login/attachments/ui-design.png`
