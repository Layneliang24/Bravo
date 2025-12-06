# Task ID: 3

**Title:** 后端：用户注册API实现

**Status:** pending

**Dependencies:** 1, 2

**Priority:** high

**Description:** 实现用户注册API (`POST /api/auth/register/`)，包括邮箱注册、密码强度验证、动态验证码验证和注册成功后JWT Token生成。

**Details:**

1. **红（Red）**：编写测试用例，覆盖注册成功、邮箱已存在、密码不符合强度、验证码错误等场景，预期测试失败。2. **绿（Green）**：在`backend/apps/users/serializers.py`中创建注册序列化器，包含邮箱、密码、确认密码、验证码ID和答案字段。在`backend/apps/users/views.py`中实现`POST /api/auth/register/`视图，验证邮箱唯一性，使用Django内置PBKDF2哈希密码，验证密码强度（最少8位，包含字母和数字），验证动态验证码。注册成功后，生成JWT Access Token和Refresh Token，并返回用户基本信息。3. **重构（Refactor）**：优化序列化器和视图逻辑，确保错误处理清晰。

**Test Strategy:**

编写`backend/tests/unit/test_auth_views.py`单元测试，测试注册视图的输入验证、密码哈希、用户创建、Token生成等逻辑。编写`backend/tests/integration/test_auth_api.py`集成测试，测试完整的注册流程，包括成功注册、重复注册、密码强度不足、验证码错误等场景。

## Subtasks

### 3.1. 编写注册API的集成测试用例 (Red)

**Status:** pending
**Dependencies:** None

根据需求，在`backend/tests/integration/test_auth_api.py`中为注册API (`POST /api/auth/register/`) 编写初始的集成测试用例，覆盖成功、邮箱已存在、密码弱、验证码错误等场景。这些测试在实现功能前预期会失败。

**Details:**

创建测试类 `TestRegisterAPI`。编写测试方法 `test_register_success`, `test_register_email_exists`, `test_register_weak_password`, `test_register_invalid_captcha`。使用 Django REST Framework 的 `APIClient` 来模拟请求。

### 3.2. 创建用户注册序列化器 (UserRegisterSerializer)

**Status:** pending
**Dependencies:** 3.1

在 `backend/apps/users/serializers.py` 文件中创建一个名为 `UserRegisterSerializer` 的序列化器，用于处理注册请求的数据验证，包括邮箱、密码、确认密码和验证码信息。

**Details:**

序列化器应继承自 `serializers.Serializer`。包含 `email`, `password`, `password2` (用于确认密码), `captcha_id`, `captcha_answer` 字段。`email` 字段应验证唯一性。`password` 字段应为 `write_only=True`。添加 `validate` 方法来检查两次输入的密码是否一致，并验证密码强度（最少8位，包含字母和数字）。

### 3.3. 实现注册API视图 (RegisterAPIView)

**Status:** pending
**Dependencies:** 3.2

在 `backend/apps/users/views.py` 中创建处理 `POST /api/auth/register/` 请求的视图。该视图将使用 `UserRegisterSerializer` 来验证输入数据，验证验证码，并创建新用户。

**Details:**

创建一个基于 `generics.GenericAPIView` 的视图，并设置 `serializer_class = UserRegisterSerializer`。在 `post` 方法中，首先验证序列化器数据。然后，调用一个独立的工具函数来验证验证码的正确性（依赖任务2）。如果所有验证通过，则创建新用户实例，并使用 `user.set_password()` 方法对密码进行哈希处理后保存。

### 3.4. 集成JWT并为新用户生成Tokens

**Status:** pending
**Dependencies:** 3.3

在用户成功注册并创建后，为新用户生成 JWT Access Token 和 Refresh Token，并将其包含在成功的API响应中。

**Details:**

在注册视图成功创建用户的逻辑分支中，使用 `rest_framework_simplejwt.tokens.RefreshToken.for_user(user)` 方法为新用户生成 tokens。将 `access` 和 `refresh` tokens 以及用户基本信息（如邮箱、用户ID）组织成一个字典，并作为 `Response` 返回，HTTP状态码为 `201 Created`。

### 3.5. 重构代码并确保所有测试通过 (Refactor)

**Status:** pending
**Dependencies:** 3.4

优化注册序列化器和视图的代码结构，改善错误处理逻辑，确保代码清晰可维护，并最终确保所有在第一步中编写的测试用例都能成功通过。

**Details:**

审查 `UserRegisterSerializer` 和注册视图的代码，将复杂的逻辑（如密码强度验证）提取到独立的工具函数中。统一API的错误响应格式。完整运行 `pytest` 命令，确认 `test_auth_api.py` 和 `test_auth_serializers.py` 中的所有测试用例都通过。
