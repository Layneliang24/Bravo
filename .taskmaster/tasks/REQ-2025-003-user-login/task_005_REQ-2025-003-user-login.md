# Task ID: 5

**Title:** 后端：JWT Token管理API实现

**Status:** pending

**Dependencies:** 4

**Priority:** medium

**Description:** 实现JWT Token的刷新 (`POST /api/auth/token/refresh/`) 和登出 (`POST /api/auth/logout/`) 功能。

**Details:**

1. **红（Red）**：编写测试用例，验证Token刷新成功、使用过期Refresh Token刷新失败、登出成功等场景，预期测试失败。2. **绿（Green）：**集成`djangorestframework-simplejwt`。在`backend/apps/users/views.py`中实现`POST /api/auth/token/refresh/`视图，接收Refresh Token并返回新的Access Token。实现`POST /api/auth/logout/`视图，使当前Access Token失效。3. **重构（Refactor）**：优化Token处理逻辑，确保安全和效率。

**Test Strategy:**

编写`backend/tests/integration/test_auth_api.py`集成测试，测试Token刷新机制是否正常工作，登出后Access Token是否失效。

## Subtasks

### 5.1. 编写JWT Token刷新与登出API的集成测试用例

**Status:** pending
**Dependencies:** None

按照TDD的“红”阶段要求，在`backend/tests/integration/test_auth_api.py`中编写测试用例，覆盖Token刷新成功、使用过期Refresh Token刷新失败、登出成功、登出后Access Token失效等场景。预期这些测试在功能未实现前会失败。

**Details:**

创建或修改`backend/tests/integration/test_auth_api.py`文件，并添加测试方法，例如`test_token_refresh_success`、`test_token_refresh_with_expired_refresh_token`、`test_logout_success`、`test_access_token_invalid_after_logout`。确保测试用例能够模拟HTTP请求并断言预期的响应和状态码。

### 5.2. 集成`djangorestframework-simplejwt`库

**Status:** pending
**Dependencies:** None

在Django项目中安装并配置`djangorestframework-simplejwt`库，使其能够处理JWT Token的生成、验证和刷新机制。

**Details:**

在`backend/requirements.txt`中添加`djangorestframework-simplejwt`依赖，并运行`pip install -r requirements.txt`。在`backend/config/settings.py`中配置`REST_FRAMEWORK`以使用`simplejwt`的认证类，并配置`SIMPLE_JWT`设置，例如Access Token和Refresh Token的生命周期。

### 5.3. 实现JWT Token刷新API (`POST /api/auth/token/refresh/`)

**Status:** pending
**Dependencies:** 5.2

在`backend/apps/users/views.py`中实现`POST /api/auth/token/refresh/`视图，该视图接收一个Refresh Token，并返回一个新的Access Token和Refresh Token。

**Details:**

在`backend/apps/users/views.py`中创建一个新的视图类，继承自`TokenRefreshView`或自定义视图，处理传入的Refresh Token。验证Refresh Token的有效性，并生成新的Access Token和Refresh Token作为响应。确保API端点在`backend/apps/users/urls.py`中正确注册。

### 5.4. 实现用户登出API (`POST /api/auth/logout/`)

**Status:** pending
**Dependencies:** 5.2

在`backend/apps/users/views.py`中实现`POST /api/auth/logout/`视图，该视图使当前用户的Refresh Token失效，从而实现登出功能。

**Details:**

在`backend/apps/users/views.py`中创建一个新的视图类，继承自`TokenBlacklistView`或自定义视图。该视图应接收Refresh Token（或通过认证头获取），并将其加入黑名单，使其失效。确保API端点在`backend/apps/users/urls.py`中正确注册。

### 5.5. 优化Token处理逻辑并确保所有测试通过

**Status:** pending
**Dependencies:** 5.1, 5.3, 5.4

对已实现的Token刷新和登出逻辑进行代码审查和重构，确保其安全、高效且符合最佳实践。运行所有相关的集成测试，确保所有测试用例通过。

**Details:**

检查Token的生命周期管理、黑名单机制、错误处理和响应格式。优化数据库查询和Redis操作（如果适用）。运行`python manage.py test backend/tests/integration/test_auth_api.py`，修复所有失败的测试，直到所有测试通过。
