# Task ID: 15

**Title:** 前端：用户预览组件开发与登录表单集成

**Status:** pending

**Dependencies:** 8, 9, 11, 12

**Priority:** high

**Description:** 开发`UserPreview.vue`组件，并在`auth` store中实现登录预验证动作，将其集成到`LoginForm.vue`中。

**Details:**

1. **红（Red）**：编写组件测试，验证`UserPreview`在不同状态（加载中、有效、无效、无头像）下的显示。编写store测试，验证`previewLogin` action的调用和`preview`状态的更新。编写集成测试，验证`LoginForm`中预验证的触发和`UserPreview`的显示。预期测试失败。2. **绿（Green）**：在`frontend/src/components/auth/`目录下创建`UserPreview.vue`，显示圆形头像（真实头像或首字母默认头像）、用户显示名称，支持加载中状态和淡入动画。在`frontend/src/stores/auth.ts`的`AuthState`中添加`preview`状态，实现`previewLogin` action，调用后端`/api/auth/preview/`接口，并更新`preview`状态。在`LoginForm.vue`中，监听密码输入框的失焦事件或停止输入500ms后触发`previewLogin` action，并将`UserPreview.vue`集成到表单上方。3. **重构（Refactor）**：优化组件的动画效果和与store的交互逻辑。

**Test Strategy:**

编写`frontend/src/components/auth/__tests__/UserPreview.spec.ts`组件测试。编写`frontend/src/stores/__tests__/auth.spec.ts`单元测试，模拟`previewLogin`的API响应。编写`e2e/tests/auth/login-preview.spec.ts`E2E测试，验证登录预验证的触发、头像显示、默认头像显示、错误处理和频率限制。

## Subtasks

### 15.1. 开发UserPreview组件及其单元测试

**Status:** pending
**Dependencies:** None

在`frontend/src/components/auth/`目录下创建`UserPreview.vue`组件，实现圆形头像（真实头像或首字母默认头像）、用户显示名称，支持加载中状态和淡入动画。同时，编写组件测试，验证`UserPreview`在不同状态（加载中、有效、无效、无头像）下的显示。

**Details:**

创建`frontend/src/components/auth/UserPreview.vue`。实现Vue组件的模板、样式和逻辑，以显示用户头像和名称。头像应支持加载中状态和淡入动画。编写`frontend/src/components/auth/__tests__/UserPreview.spec.ts`，使用Vue Test Utils模拟不同props和状态，验证组件的渲染和行为。

### 15.2. 实现auth store的预验证状态和动作及其单元测试

**Status:** pending
**Dependencies:** None

在`frontend/src/stores/auth.ts`的`AuthState`中添加`preview`状态，并实现`previewLogin` action。该action将调用后端`/api/auth/preview/`接口，并根据接口响应更新`preview`状态。同时，编写store单元测试，验证`previewLogin` action的调用和`preview`状态的更新。

**Details:**

修改`frontend/src/stores/auth.ts`，添加`preview`状态（例如，一个包含用户数据或错误信息的对象）。实现`previewLogin`异步action，使用`axios`或其他HTTP客户端调用`/api/auth/preview/`接口。处理API响应，更新`preview`状态。编写`frontend/src/stores/__tests__/auth.spec.ts`，模拟API调用，验证`previewLogin` action的逻辑和状态更新。

### 15.3. 将UserPreview集成到LoginForm并触发预验证

**Status:** pending
**Dependencies:** 15.1, 15.2, 15.12

在`LoginForm.vue`中，监听密码输入框的失焦事件或停止输入500ms后触发`previewLogin` action。将`UserPreview.vue`组件集成到`LoginForm`的表单上方，并根据`auth` store的`preview`状态显示用户预览信息。同时，编写集成测试，验证`LoginForm`中预验证的触发和`UserPreview`的显示。

**Details:**

修改`frontend/src/components/auth/LoginForm.vue`。在密码输入框上添加事件监听器（例如`@blur`或使用`debounce`处理`@input`事件），在满足条件时调用`auth` store的`previewLogin` action。在`LoginForm`模板中引入并使用`UserPreview`组件，通过props将`auth` store中的`preview`状态传递给`UserPreview`。编写集成测试，验证`LoginForm`的交互逻辑。

### 15.4. 优化UserPreview组件动画与store交互

**Status:** pending
**Dependencies:** 15.1, 15.3

审查并优化`UserPreview.vue`组件的淡入动画效果，确保用户体验流畅。同时，优化`UserPreview`组件与`auth` store之间的数据流和交互逻辑，减少不必要的渲染或提高响应速度。

**Details:**

检查`UserPreview.vue`中的CSS动画或Vue过渡效果，进行调整以达到最佳视觉效果。分析组件的`props`、`computed`属性和`watchers`，确保与`auth` store的`preview`状态同步高效。考虑使用`v-memo`或`keep-alive`等Vue优化策略（如果适用）。

### 15.5. 编写端到端（E2E）测试

**Status:** pending
**Dependencies:** 15.3

编写E2E测试，验证完整的登录预验证流程。包括验证用户在密码输入后预验证是否触发、`UserPreview`组件是否正确显示用户头像（真实头像或默认头像）、错误处理是否正确显示以及频率限制是否生效。

**Details:**

在`e2e/tests/auth/`目录下创建`login-preview.spec.ts`。使用Cypress或Playwright等E2E测试框架，模拟用户访问登录页面、输入用户名和密码、触发预验证。断言`UserPreview`组件的可见性、显示内容（头像URL、显示名称）、加载状态和错误提示。模拟后端响应以测试频率限制等场景。
