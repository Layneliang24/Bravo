# Task ID: 9

**Title:** 前端：基础UI组件开发 (FloatingInput, DefaultAvatar)

**Status:** pending

**Dependencies:** None

**Priority:** medium

**Description:** 开发可复用的悬浮式输入框组件 (`FloatingInput.vue`) 和默认头像组件 (`DefaultAvatar.vue`)。

**Details:**

1. **红（Red）**：编写组件测试，验证`FloatingInput`的标签上浮动画、错误状态显示、图标支持。验证`DefaultAvatar`在有/无`avatar_url`时显示正确头像或首字母。预期测试失败。2. **绿（Green）**：在`frontend/src/components/auth/`目录下创建`FloatingInput.vue`，实现输入时标签上浮动画、错误状态显示、图标支持。创建`DefaultAvatar.vue`，根据传入的`avatar_url`显示真实头像，若无则根据`avatar_letter`显示首字母生成的默认头像。使用Tailwind CSS / 自定义CSS进行样式设计。3. **重构（Refactor）**：优化组件的props、事件和样式，确保可复用性和性能。

**Test Strategy:**

编写`frontend/src/components/auth/__tests__/FloatingInput.spec.ts`和`frontend/src/components/auth/__tests__/DefaultAvatar.spec.ts`组件测试，验证组件的渲染、交互和状态更新。

## Subtasks

### 9.1. 编写 FloatingInput 组件测试 (Red)

**Status:** pending
**Dependencies:** None

编写 `FloatingInput.vue` 组件的单元测试，验证其标签上浮动画、错误状态显示和图标支持功能。预期这些测试在组件未实现时会失败。

**Details:**

在 `frontend/src/components/auth/__tests__/FloatingInput.spec.ts` 中创建测试文件。使用 Vue Test Utils 模拟用户输入、聚焦/失焦事件，断言标签的 CSS 类变化、错误消息的显示以及图标的渲染。确保测试覆盖所有关键交互和状态。

### 9.2. 编写 DefaultAvatar 组件测试 (Red)

**Status:** pending
**Dependencies:** None

编写 `DefaultAvatar.vue` 组件的单元测试，验证其在有 `avatar_url` 时显示真实头像，无 `avatar_url` 时根据 `avatar_letter` 显示首字母默认头像。预期这些测试在组件未实现时会失败。

**Details:**

在 `frontend/src/components/auth/__tests__/DefaultAvatar.spec.ts` 中创建测试文件。使用 Vue Test Utils 模拟传入不同 `avatar_url` 和 `avatar_letter` props 的情况，断言 `<img>` 标签的 `src` 属性或显示首字母的 `<span>` 元素内容是否正确。

### 9.3. 实现 FloatingInput 组件 (Green)

**Status:** pending
**Dependencies:** 9.1

在 `frontend/src/components/auth/` 目录下创建并实现 `FloatingInput.vue` 组件，包括标签上浮动画、错误状态显示和图标支持，并确保通过所有相关测试。

**Details:**

使用 Vue 3 Composition API 实现组件逻辑。利用 Tailwind CSS 或自定义 CSS 实现样式。确保输入框聚焦时标签上浮，输入内容后标签保持上浮。根据 `error` prop 显示错误样式和消息。支持通过 prop 传入图标。运行并确保通过 `FloatingInput` 的所有测试。

### 9.4. 实现 DefaultAvatar 组件 (Green)

**Status:** pending
**Dependencies:** 9.2

在 `frontend/src/components/auth/` 目录下创建并实现 `DefaultAvatar.vue` 组件，根据 `avatar_url` 或 `avatar_letter` 显示头像，并确保通过所有相关测试。

**Details:**

使用 Vue 3 Composition API 实现组件逻辑。如果传入 `avatar_url`，则显示图片；否则，根据 `avatar_letter` 生成并显示首字母头像。使用 Tailwind CSS 或自定义 CSS 进行样式设计，确保头像的圆形显示和居中对齐。运行并确保通过 `DefaultAvatar` 的所有测试。

### 9.5. 优化 FloatingInput 和 DefaultAvatar 组件 (Refactor)

**Status:** pending
**Dependencies:** 9.3, 9.4

对 `FloatingInput` 和 `DefaultAvatar` 组件的 props、事件和样式进行优化，提高组件的可复用性、可维护性和性能，同时确保现有测试通过。

**Details:**

审查组件的 props 定义，确保命名清晰、类型正确且默认值合理。优化事件发射机制。检查并精简 CSS 样式，移除冗余代码，提高性能。确保组件在不同场景下都能良好工作，并考虑无障碍性。重构后需再次运行所有相关测试，确保功能无回归。
