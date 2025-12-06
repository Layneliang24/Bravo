# Task ID: 12

**Title:** 前端：登录表单开发与集成

**Status:** pending

**Dependencies:** 11

**Priority:** high

**Description:** 开发`LoginForm.vue`，集成`FloatingInput`和`Captcha`组件，并与`auth` store的登录动作进行集成。

**Details:**

1. **红（Red）**：编写组件测试，验证`LoginForm`的渲染、表单验证、提交逻辑、错误提示和验证码刷新。预期测试失败。2. **绿（Green）**：在`frontend/src/components/auth/`目录下创建`LoginForm.vue`。使用`FloatingInput`组件处理邮箱和密码输入，使用`Captcha`组件处理验证码。集成VeeValidate进行表单验证。通过Pinia `auth` store调用`login` action。处理登录失败时的错误提示和验证码刷新。3. **重构（Refactor）**：优化表单的交互逻辑和错误处理。

**Test Strategy:**

编写`frontend/src/components/auth/__tests__/LoginForm.spec.ts`组件测试，模拟用户输入和提交，验证表单的行为和与store的交互。编写E2E测试，验证完整的登录流程。

## Subtasks

### 12.1. 创建LoginForm骨架并集成FloatingInput

**Status:** pending
**Dependencies:** 12.9

在`frontend/src/components/auth/`目录下创建`LoginForm.vue`文件，并集成`FloatingInput`组件用于邮箱和密码输入字段。

**Details:**

在`frontend/src/components/auth/`目录下创建`LoginForm.vue`。引入`FloatingInput`组件，并将其用于邮箱和密码的输入字段。确保组件能够正确渲染，并且`FloatingInput`的基本功能（如标签上浮）正常工作。

### 12.2. 集成Captcha组件与基础表单结构

**Status:** pending
**Dependencies:** 12.1

在`LoginForm.vue`中集成`Captcha`组件，并构建包含邮箱、密码和验证码输入的基础HTML表单结构。

**Details:**

在`LoginForm.vue`中引入并集成`Captcha`组件。构建一个完整的`<form>`元素，包含邮箱输入（使用`FloatingInput`）、密码输入（使用`FloatingInput`）、验证码输入（使用`Captcha`）以及一个提交按钮。实现一个空的表单提交方法，为后续逻辑集成做准备。

### 12.3. 实现表单验证逻辑 (VeeValidate)

**Status:** pending
**Dependencies:** 12.2

使用VeeValidate库为`LoginForm.vue`中的邮箱、密码和验证码字段实现客户端验证规则，并显示相应的错误信息。

**Details:**

在`LoginForm.vue`中集成VeeValidate。为邮箱字段添加有效的邮箱格式验证规则。为密码字段添加最小长度（例如8位）和必填验证。为验证码字段添加必填验证。配置VeeValidate以在用户输入无效时显示错误提示信息。

### 12.4. 集成Pinia Auth Store登录动作与错误处理

**Status:** pending
**Dependencies:** 12.3

将`LoginForm`与Pinia `auth` store的`login` action进行集成，处理登录成功后的导航、登录失败时的错误提示和验证码刷新。

**Details:**

在`LoginForm.vue`中，通过Pinia `useAuthStore`调用`login` action，将表单的邮箱、密码和验证码数据作为参数传递。处理`login` action返回的成功或失败结果。登录成功后，执行页面导航（例如，跳转到仪表盘）。登录失败时，捕获错误信息，显示用户友好的错误提示，并触发`Captcha`组件刷新验证码。

### 12.5. 编写组件测试与表单重构优化

**Status:** pending
**Dependencies:** 12.4

为`LoginForm.vue`编写全面的组件测试，覆盖渲染、表单验证、提交逻辑、错误提示和验证码刷新。根据测试结果和最佳实践，对表单的交互逻辑和代码结构进行重构和优化。

**Details:**

在`frontend/src/components/auth/__tests__/LoginForm.spec.ts`中编写组件测试。测试用例应包括：组件的正确渲染、输入有效/无效数据时的验证行为、成功提交后的行为、提交失败时的错误提示和验证码刷新机制。根据测试覆盖率和代码审查，优化表单的交互逻辑、错误消息的显示方式、状态管理和代码可读性。
