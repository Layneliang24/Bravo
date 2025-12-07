# Task ID: 13

**Title:** 前端：注册表单开发与集成

**Status:** pending

**Dependencies:** 11

**Priority:** high

**Description:** 开发`RegisterForm.vue`，集成`FloatingInput`、`Captcha`和`PasswordStrength`组件，并与`auth` store的注册动作进行集成。

**Details:**

1. **红（Red）**：编写组件测试，验证`RegisterForm`的渲染、表单验证、密码强度显示、提交逻辑、错误提示和验证码刷新。预期测试失败。2. **绿（Green）**：在`frontend/src/components/auth/`目录下创建`RegisterForm.vue`。使用`FloatingInput`处理邮箱、密码和确认密码输入，使用`Captcha`组件处理验证码，集成`PasswordStrength`组件显示密码强度。通过Pinia `auth` store调用`register` action。处理注册失败时的错误提示和验证码刷新。3. **重构（Refactor）**：优化表单的交互逻辑和错误处理。

**Test Strategy:**

编写`frontend/src/components/auth/__tests__/RegisterForm.spec.ts`组件测试，模拟用户输入和提交，验证表单的行为和与store的交互。编写E2E测试，验证完整的注册流程。

## Subtasks

### 13.1. 编写 `RegisterForm` 组件测试骨架

**Status:** pending
**Dependencies:** None

创建 `RegisterForm.spec.ts` 文件，编写测试用例以验证组件的渲染、表单验证规则、密码强度显示、提交逻辑、错误提示和验证码刷新。预期这些测试最初会失败。

**Details:**

在 `frontend/src/components/auth/__tests__/` 目录下创建 `RegisterForm.spec.ts`。使用 Vue Test Utils 编写测试，模拟用户输入，断言组件状态和渲染输出。重点关注表单字段的存在、验证消息、密码强度组件的显示、提交按钮状态以及错误提示的显示。

### 13.2. 开发 `RegisterForm` 基础结构与 `FloatingInput` 集成

**Status:** pending
**Dependencies:** 13.9

在 `frontend/src/components/auth/` 目录下创建 `RegisterForm.vue`，并使用 `FloatingInput` 组件实现邮箱、密码和确认密码的输入字段。

**Details:**

创建 `RegisterForm.vue` 文件。定义表单的响应式数据模型（例如，email, password, confirmPassword）。集成 `FloatingInput` 组件，为邮箱、密码和确认密码创建输入框，并绑定到数据模型。实现基本的客户端表单验证逻辑（例如，邮箱格式、密码长度、两次密码一致性）。

### 13.3. 集成 `PasswordStrength` 和 `Captcha` 组件

**Status:** pending
**Dependencies:** 13.2

将 `PasswordStrength` 组件集成到密码输入字段下方以显示密码强度，并集成 `Captcha` 组件以处理验证码的显示和输入。

**Details:**

在 `RegisterForm.vue` 中，将 `PasswordStrength` 组件放置在密码输入框下方，并将其 `password` 属性绑定到表单的密码字段。集成 `Captcha` 组件，处理验证码的显示、用户输入和刷新机制。确保验证码组件能够获取新的验证码ID和图片。

### 13.4. 实现 `auth` store 注册逻辑与错误处理

**Status:** pending
**Dependencies:** 13.3

将表单提交逻辑与 Pinia `auth` store 的 `register` action 进行集成，并处理注册成功与失败的响应，包括错误提示和验证码刷新。

**Details:**

在 `RegisterForm.vue` 中，创建一个提交方法，该方法将收集表单数据（邮箱、密码、确认密码、验证码ID和答案）。通过 Pinia `auth` store 调用 `register` action，并传递表单数据。根据 `register` action 的返回结果，显示成功消息或处理注册失败时的错误提示（例如，邮箱已存在、密码强度不足、验证码错误）。在注册失败时，触发 `Captcha` 组件的刷新。

### 13.5. 优化表单交互、错误处理与测试验证

**Status:** pending
**Dependencies:** 13.1, 13.2, 13.3, 13.4

优化 `RegisterForm` 的用户体验，包括表单的交互逻辑、错误提示的清晰度、加载状态的显示，并确保所有组件测试和E2E测试通过。

**Details:**

审查并改进表单的UI/UX，例如在提交过程中禁用按钮、显示加载指示器。确保所有验证消息和后端错误提示都以用户友好的方式显示。运行并确保所有为 `RegisterForm` 编写的组件测试通过。如果需要，编写或更新E2E测试以验证完整的注册流程。
