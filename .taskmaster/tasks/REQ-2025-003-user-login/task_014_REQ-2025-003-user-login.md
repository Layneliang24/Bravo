# Task ID: 14

**Title:** 前端：密码找回表单开发与集成

**Status:** pending

**Dependencies:** 11

**Priority:** medium

**Description:** 开发密码找回相关表单，包括发送重置邮件表单和重置密码表单，并与`auth` store的相应动作进行集成。

**Details:**

1. **红（Red）**：编写组件测试，验证发送重置邮件表单的提交、错误提示。验证重置密码表单的提交、密码强度、错误提示。预期测试失败。2. **绿（Green）**：在`frontend/src/components/auth/`目录下创建`PasswordResetForm.vue`用于发送重置邮件，集成`FloatingInput`和`Captcha`，通过`auth` store调用`sendPasswordReset` action。创建单独的重置密码页面/组件，接收URL中的token，集成`FloatingInput`和`PasswordStrength`，通过`auth` store调用`resetPassword` action。3. **重构（Refactor）**：优化表单的交互逻辑和错误处理。

**Test Strategy:**

编写`frontend/src/components/auth/__tests__/PasswordResetForm.spec.ts`组件测试，验证表单的渲染、提交和与store的交互。编写E2E测试，验证完整的密码找回流程。

## Subtasks

### 14.1. 实现`auth` store中的密码重置请求动作

**Status:** pending
**Dependencies:** 14.11

在`auth` store中添加或修改`sendPasswordReset` action，使其能够调用后端API发送密码重置邮件。这是前端表单提交的基础。

**Details:**

在`frontend/src/store/auth.js`中定义`sendPasswordReset` action。该action应接收用户邮箱和验证码作为参数，并调用后端`/api/auth/password/reset/request/`接口。需要处理API响应，包括成功和错误情况。

### 14.2. 开发发送密码重置邮件表单组件

**Status:** pending
**Dependencies:** 14.1, 14.2

在前端创建`PasswordResetForm.vue`组件，用于收集用户邮箱和验证码，并触发密码重置邮件发送。

**Details:**

在`frontend/src/components/auth/`目录下创建`PasswordResetForm.vue`。集成`FloatingInput`用于邮箱输入，集成`Captcha`组件用于验证码输入。表单提交时，调用`auth` store的`sendPasswordReset` action。需要实现客户端表单验证和错误提示。

### 14.3. 实现`auth` store中的密码重置确认动作

**Status:** pending
**Dependencies:** 14.11

在`auth` store中添加或修改`resetPassword` action，使其能够调用后端API完成密码重置。这是重置密码页面提交的基础。

**Details:**

在`frontend/src/store/auth.js`中定义`resetPassword` action。该action应接收token、新密码和确认密码作为参数，并调用后端`/api/auth/password/reset/confirm/`接口。需要处理API响应，包括成功和错误情况。

### 14.4. 开发重置密码页面/组件

**Status:** pending
**Dependencies:** 14.3

创建一个独立的页面或组件，用于用户通过重置链接访问时输入新密码并完成密码重置。

**Details:**

创建一个路由（例如`/reset-password?token=...`）和对应的Vue组件。组件应从URL中获取`token`参数。集成`FloatingInput`用于新密码和确认密码输入，集成`PasswordStrength`组件显示密码强度。表单提交时，调用`auth` store的`resetPassword` action。需要实现客户端表单验证、密码强度显示和错误提示。

### 14.5. 编写密码找回流程的组件与E2E测试

**Status:** pending
**Dependencies:** 14.2, 14.4

编写针对发送重置邮件表单和重置密码页面的组件测试，并编写端到端测试以验证完整的密码找回流程。

**Details:**

完善`frontend/src/components/auth/__tests__/PasswordResetForm.spec.ts`，确保覆盖发送重置邮件表单的提交、错误提示、验证码交互等场景。为重置密码页面/组件编写组件测试，验证其提交、密码强度、错误提示、token处理等场景。编写E2E测试（例如在`e2e/tests/auth/password-reset.spec.ts`），模拟用户从请求重置邮件到点击链接、输入新密码并成功重置的完整流程。
