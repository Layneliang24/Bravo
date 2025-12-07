# Task ID: 11

**Title:** 前端：Pinia Auth Store核心实现

**Status:** pending

**Dependencies:** 5, 6, 7, 10

**Priority:** high

**Description:** 在Pinia中实现`auth` store，定义认证相关的状态和核心动作，包括登录、注册、登出、Token刷新、验证码获取和刷新。

**Details:**

1. **红（Red）**：编写store测试，验证`auth` store的状态初始化、`login`、`register`、`logout`、`refreshToken`、`fetchCaptcha`、`refreshCaptcha`等action的调用和状态更新。预期测试失败。2. **绿（Green）**：在`frontend/src/stores/auth.ts`中定义`AuthState`接口，包含`user`, `token`, `refreshToken`, `isAuthenticated`, `captcha`等状态。定义`AuthActions`接口，实现`login`, `register`, `logout`, `refreshToken`, `fetchCaptcha`, `refreshCaptcha`等异步action，使用Axios调用后端API。处理Token的存储（例如localStorage或sessionStorage）和`isAuthenticated`状态的更新。3. **重构（Refactor）**：优化store的模块化和错误处理，确保状态管理清晰。

**Test Strategy:**

编写`frontend/src/stores/__tests__/auth.spec.ts`单元测试，模拟API请求，验证store的状态管理和action的正确性。

## Subtasks

### 11.1. 编写Pinia Auth Store初始测试

**Status:** pending
**Dependencies:** None

编写`auth` store的单元测试，验证其初始状态、`login`、`register`、`logout`、`refreshToken`、`fetchCaptcha`、`refreshCaptcha`等核心action的调用和状态更新逻辑。预期测试失败。

**Details:**

在`frontend/src/stores/__tests__/auth.spec.ts`中创建测试文件。编写测试用例，验证`auth` store的初始状态是否正确。为`login`、`register`、`logout`、`refreshToken`、`fetchCaptcha`、`refreshCaptcha`等action编写测试桩，模拟API调用，并断言store状态的预期变化。确保测试在store未实现时失败。

### 11.2. 定义Auth Store状态接口与基本结构

**Status:** pending
**Dependencies:** 11.1

在Pinia中定义`auth` store的初始状态接口(`AuthState`)和动作接口(`AuthActions`)，并设置store的基本结构。

**Details:**

在`frontend/src/stores/auth.ts`中定义`AuthState`接口，包含`user`, `token`, `refreshToken`, `isAuthenticated`, `captcha`等状态字段及其类型。定义`AuthActions`接口，声明`login`, `register`, `logout`, `refreshToken`, `fetchCaptcha`, `refreshCaptcha`等异步action的签名。初始化`auth` store，设置其`id`和初始状态。

### 11.3. 实现Auth Store的登录、注册和登出功能

**Status:** pending
**Dependencies:** 11.2, 11.5, 11.10

在`auth` store中实现用户登录、注册和登出功能，包括调用后端API、处理Token存储和`isAuthenticated`状态更新。

**Details:**

在`frontend/src/stores/auth.ts`中实现`login` action，使用Axios调用后端登录API，成功后将`token`和`refreshToken`存储到`localStorage`或`sessionStorage`，并更新`user`和`isAuthenticated`状态。实现`register` action，调用后端注册API。实现`logout` action，清除存储的Token，重置`user`和`isAuthenticated`状态。

### 11.4. 实现Auth Store的Token刷新和验证码功能

**Status:** pending
**Dependencies:** 11.3, 11.2, 11.6, 11.10

在`auth` store中实现Token刷新、获取验证码和刷新验证码的异步动作，并处理相关状态更新。

**Details:**

在`frontend/src/stores/auth.ts`中实现`refreshToken` action，使用`refreshToken`调用后端API获取新的`token`和`refreshToken`，并更新存储和状态。实现`fetchCaptcha` action，调用后端API获取验证码图片和ID，更新`captcha`状态。实现`refreshCaptcha` action，调用后端API刷新验证码。

### 11.5. 优化Auth Store的模块化与错误处理

**Status:** pending
**Dependencies:** 11.4

对`auth` store进行重构，优化其模块化结构和错误处理机制，确保状态管理清晰、代码健壮。

**Details:**

审查`auth` store的代码，确保逻辑分离清晰，例如将API调用逻辑封装到单独的服务层。实现统一的错误处理机制，捕获API请求中的错误，并向用户提供友好的反馈。考虑使用Pinia插件或中间件来增强store的功能。确保所有状态更新都是响应式的。
