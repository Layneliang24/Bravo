# Task ID: 8

**Title:** 后端：登录预验证API与频率限制

**Status:** pending

**Dependencies:** 1, 2, 4

**Priority:** high

**Description:** 实现登录预验证API (`POST /api/auth/preview/`)，用于在不实际登录的情况下验证账号密码并返回用户头像信息，并实施频率限制。

**Details:**

1. **红（Red）**：编写测试用例，验证正确账号密码返回头像信息、错误账号密码返回`valid: false`、无头像用户返回默认头像信息、以及频率限制生效的场景，预期测试失败。2. **绿（Green）**：在`backend/apps/users/views.py`中实现`POST /api/auth/preview/`视图。该接口需验证码保护。验证邮箱和密码是否匹配，但不执行实际登录。如果匹配，返回`valid: true`以及用户的`display_name`、`avatar_url`（或`null`）、`default_avatar`（布尔值）、`avatar_letter`（首字母）。如果用户没有设置头像，则根据`display_name`或`username`的首字母生成`avatar_letter`。无论成功失败，均返回200状态码，通过`valid`字段区分。在`backend/apps/users/throttling.py`中实现自定义频率限制，限制同一IP每分钟最多10次请求。3. **重构（Refactor）**：优化预验证逻辑和响应结构，确保安全性和性能。

**Test Strategy:**

编写`backend/tests/unit/test_auth_preview.py`单元测试，测试预验证逻辑在不同账号密码和头像情况下的响应。编写`backend/tests/integration/test_preview_throttling.py`集成测试，测试预验证API的频率限制是否生效，以及在限制下的行为。

## Subtasks

### 8.1. 编写登录预验证API的单元测试

**Status:** pending
**Dependencies:** 8.1

编写针对登录预验证API (`POST /api/auth/preview/`) 的单元测试，覆盖正确/错误账号密码、有/无头像用户、以及频率限制的场景，预期测试失败。

**Details:**

在`backend/tests/unit/test_auth_preview.py`中创建测试用例，模拟`POST /api/auth/preview/`请求。测试用例应验证不同输入下的预期响应结构、`valid`字段、`display_name`、`avatar_url`、`default_avatar`和`avatar_letter`字段。同时，编写频率限制的集成测试，预期在未实现功能前测试失败。

### 8.2. 实现登录预验证API基础逻辑与响应

**Status:** pending
**Dependencies:** 8.1, 8.1

在`backend/apps/users/views.py`中实现`POST /api/auth/preview/`视图的基础框架，包括邮箱密码验证、用户头像信息（`avatar_url`, `default_avatar`, `avatar_letter`）的获取和响应。

**Details:**

创建`PreviewLoginAPIView`，处理`POST`请求。验证邮箱和密码是否匹配（不执行实际登录）。根据用户`avatar`字段判断`avatar_url`，如果为空则根据`display_name`或`username`的首字母生成`avatar_letter`。返回`display_name`、`avatar_url`、`default_avatar`、`avatar_letter`和`valid`字段。无论成功失败，均返回200状态码。

### 8.3. 实现登录预验证API频率限制

**Status:** pending
**Dependencies:** 8.2

在`backend/apps/users/throttling.py`中实现自定义频率限制，并将其应用于登录预验证API，限制同一IP每分钟最多10次请求。

**Details:**

创建`PreviewLoginThrottle`类，继承Django REST Framework的`SimpleRateThrottle`，配置`scope`和`rate`为每分钟10次。将此限制器应用于`PreviewLoginAPIView`。

### 8.4. 集成验证码保护到登录预验证API

**Status:** pending
**Dependencies:** 8.2, 8.2

将验证码保护机制集成到`POST /api/auth/preview/`接口中，确保在执行预验证逻辑前先验证验证码的有效性。

**Details:**

在`PreviewLoginAPIView`中添加验证码验证逻辑。从请求中获取`captcha_id`和`captcha_code`，调用后端验证码验证工具进行验证。验证失败时返回相应的错误信息（例如400 Bad Request或自定义错误响应）。

### 8.5. 优化预验证逻辑、响应结构与代码重构

**Status:** pending
**Dependencies:** 8.1, 8.2, 8.3, 8.4

审查并优化登录预验证API的逻辑和响应结构，确保代码的安全性、性能和可维护性。进行必要的代码重构。

**Details:**

检查`PreviewLoginAPIView`中的代码，确保异常处理完善，响应数据结构符合最佳实践。优化数据库查询，减少不必要的开销。清理冗余代码，提高代码可读性。确保所有安全最佳实践得到遵循。
