# Task ID: 4

**Title:** 后端：用户登录API实现

**Status:** pending

**Dependencies:** 1, 2, 3

**Priority:** high

**Description:** 实现用户登录API (`POST /api/auth/login/`)，包括邮箱/用户名+密码登录、动态验证码验证、登录失败次数限制和账户锁定机制。

**Details:**

1. **红（Red）**：编写测试用例，覆盖登录成功、密码错误、验证码错误、账户锁定、未激活邮箱等场景，预期测试失败。2. **绿（Green）**：在`backend/apps/users/serializers.py`中创建登录序列化器。在`backend/apps/users/views.py`中实现`POST /api/auth/login/`视图，验证邮箱/用户名和密码，验证动态验证码。实现登录失败次数跟踪（`failed_login_attempts`字段），当失败次数达到5次时，锁定账户10分钟（更新`locked_until`字段）。成功登录后重置失败次数，生成JWT Access Token和Refresh Token。3. **重构（Refactor）**：优化登录逻辑和错误响应，确保安全性和用户体验。

**Test Strategy:**

编写`backend/tests/unit/test_auth_views.py`单元测试，测试登录视图的认证逻辑、失败次数限制、账户锁定机制。编写`backend/tests/integration/test_auth_api.py`集成测试，测试完整的登录流程，包括成功登录、多次失败导致锁定、锁定期间尝试登录等场景。

## Subtasks

### 4.1. 编写用户登录API测试用例

**Status:** pending
**Dependencies:** None

编写单元测试和集成测试用例，覆盖用户登录API的各种场景，包括成功登录、密码错误、验证码错误、账户锁定、未激活邮箱等，预期测试失败。

**Details:**

在`backend/tests/unit/test_auth_views.py`中为`POST /api/auth/login/`视图编写单元测试，验证认证逻辑、失败次数限制、账户锁定机制。在`backend/tests/integration/test_auth_api.py`中编写集成测试，测试完整的登录流程，包括成功登录、多次失败导致锁定、锁定期间尝试登录等场景。

### 4.2. 实现登录序列化器与基础视图

**Status:** pending
**Dependencies:** 4.1

在`backend/apps/users/serializers.py`中创建`LoginSerializer`，并在`backend/apps/users/views.py`中实现`POST /api/auth/login/`视图的基础结构，处理请求数据解析和初步验证。

**Details:**

创建`LoginSerializer`处理`username/email`、`password`、`captcha_id`和`captcha_code`字段的输入验证。在`LoginView`中，设置允许POST请求，并使用`LoginSerializer`进行数据验证。初步验证`username/email`和`password`的格式有效性。

### 4.3. 实现核心认证与验证码验证

**Status:** pending
**Dependencies:** 4.1, 4.2

在登录视图中实现用户邮箱/用户名和密码的验证逻辑，并集成动态验证码的验证功能，处理用户未激活邮箱的情况。

**Details:**

在`LoginView`中，根据`username/email`查找用户，并验证其密码。调用Task 2提供的验证码服务（如Redis）验证`captcha_id`和`captcha_code`是否匹配且未过期。如果用户邮箱未激活，则返回相应的错误信息。

### 4.4. 实现登录失败次数限制与账户锁定

**Status:** pending
**Dependencies:** 4.1, 4.3

在登录视图中实现登录失败次数跟踪，当失败次数达到预设阈值时锁定用户账户一定时间，并在成功登录后重置失败次数。

**Details:**

检查`User`模型的`failed_login_attempts`和`locked_until`字段。如果账户已锁定，拒绝登录并返回锁定信息。每次登录失败时，增加`failed_login_attempts`计数。当计数达到5次时，更新`locked_until`字段为当前时间+10分钟。成功登录后，将`failed_login_attempts`重置为0。

### 4.5. 生成JWT Token并优化响应

**Status:** pending
**Dependencies:** 4.3, 4.4

在用户成功登录后，生成JWT Access Token和Refresh Token，将其作为响应返回。同时对登录逻辑进行错误响应优化和初步重构，确保安全性和用户体验。

**Details:**

使用JWT库生成Access Token和Refresh Token。将Token和基本用户信息（如`user_id`, `username`, `email`）作为JSON响应返回。优化所有错误响应的格式，确保一致性和清晰度。对登录视图中的代码进行初步重构，提高可读性和安全性。
