# Task ID: 16

**Title:** 前端：邮箱验证流程实现

**Status:** pending

**Dependencies:** 6, 11, 13

**Priority:** medium

**Description:** 实现前端邮箱验证流程，包括发送验证邮件的UI触发和验证链接的处理。

**Details:**

1. **红（Red）**：编写E2E测试，验证用户注册后收到验证邮件，点击链接后页面跳转并显示验证结果。预期测试失败。2. **绿（Green）**：在`auth` store中实现`sendEmailVerification`和`verifyEmail` action。在注册成功后，提示用户查收验证邮件，并提供重新发送验证邮件的UI入口。实现一个专门的路由/页面来处理邮箱验证链接（例如`/verify-email?token=...`），在该页面中调用`verifyEmail` action并显示验证结果。3. **重构（Refactor）**：优化用户提示和页面跳转逻辑。

**Test Strategy:**

编写`e2e/tests/auth/register.spec.ts`和`e2e/tests/auth/email-verification.spec.ts`E2E测试，验证注册后邮箱验证流程的完整性，包括邮件发送、链接点击和状态更新。

## Subtasks

### 16.1. 编写邮箱验证E2E测试

**Status:** pending
**Dependencies:** None

编写端到端测试，验证用户注册后收到验证邮件，点击链接后页面跳转并显示验证结果。此为红阶段测试，预期测试失败。

**Details:**

在`e2e/tests/auth/email-verification.spec.ts`中编写E2E测试用例。测试应模拟用户注册流程，检查模拟的邮件服务中是否收到验证邮件，模拟点击邮件中的验证链接，并验证页面是否正确跳转以及是否显示了预期的验证结果。预期此测试在当前阶段会失败。

### 16.2. 实现邮箱验证相关的Auth Store Action

**Status:** pending
**Dependencies:** None

在`auth` store中实现`sendEmailVerification`和`verifyEmail`两个action，用于与后端API进行交互，处理邮箱验证的发送和验证逻辑。

**Details:**

在`frontend/src/stores/auth.js`中实现`sendEmailVerification` action，该action负责调用后端发送验证邮件的API。同时，实现`verifyEmail` action，该action负责调用后端验证邮箱的API，并根据API响应更新用户状态或显示结果。

### 16.3. 实现注册成功后的邮箱验证UI提示和重发入口

**Status:** pending
**Dependencies:** 16.2

在用户注册成功后，前端页面应显示明确的提示信息，引导用户查收验证邮件，并提供一个UI入口（如按钮或链接）允许用户重新发送验证邮件。

**Details:**

修改注册成功后的页面或组件，添加一个信息提示框，告知用户已发送验证邮件，并提醒用户检查收件箱。集成一个“重新发送验证邮件”按钮，点击时调用`auth` store中的`sendEmailVerification` action，并处理发送成功或失败的反馈。

### 16.4. 实现邮箱验证链接处理页面及逻辑

**Status:** pending
**Dependencies:** 16.2

创建一个专门的路由和页面（例如`/verify-email?token=...`），用于接收邮箱验证链接中的token，调用`verifyEmail` action处理验证逻辑，并向用户显示验证结果。

**Details:**

创建`frontend/src/views/VerifyEmailView.vue`组件，并配置相应的路由`/verify-email`。在该页面中，从URL查询参数中获取`token`，然后调用`auth` store中的`verifyEmail` action。根据`verifyEmail` action的返回结果，显示邮箱验证成功或失败的消息，并提供适当的导航选项（如跳转到登录页或个人中心）。

### 16.5. 优化邮箱验证的用户提示和页面跳转逻辑

**Status:** pending
**Dependencies:** 16.3, 16.4

对整个邮箱验证流程中的用户提示信息进行优化，使其更清晰、友好，并改进页面跳转逻辑，以提升整体用户体验。

**Details:**

审查并优化注册成功后的提示信息、重新发送邮件的反馈、以及邮箱验证页面上的成功/失败提示文案，确保其清晰、易懂且具有指导性。优化验证成功或失败后的页面跳转逻辑，例如验证成功后自动跳转到用户仪表盘或登录页，验证失败后提供重试、联系支持或重新发送验证邮件的选项。
