# Task ID: 6

**Title:** 后端：邮箱验证API与异步邮件发送

**Status:** pending

**Dependencies:** 1, 5

**Priority:** high

**Description:** 实现发送邮箱验证邮件 (`POST /api/auth/email/verify/send/`) 和验证邮箱 (`GET /api/auth/email/verify/{token}/`) 的API接口，并集成Celery进行异步邮件发送。

**Details:**

1. **红（Red）**：编写测试用例，验证发送邮件API的触发、验证链接的生成、邮箱验证成功和失败（如token过期、无效）的场景，预期测试失败。2. **绿（Green）**：在`backend/apps/users/views.py`中实现`POST /api/auth/email/verify/send/`视图，生成唯一的验证Token，存储到`EmailVerification`表，并使用Celery异步发送包含验证链接的邮件。实现`GET /api/auth/email/verify/{token}/`视图，验证Token的有效性和过期时间，更新用户`is_email_verified`状态，并标记`EmailVerification`记录为已验证。3. **重构（Refactor）**：优化邮件模板、Celery任务定义和错误处理。

**Test Strategy:**

编写`backend/tests/integration/test_auth_api.py`集成测试，测试发送验证邮件API是否触发Celery任务，验证链接是否正确生成。测试邮箱验证API，验证有效Token和过期/无效Token的响应。

## Subtasks

### 6.1. 编写邮箱验证API的测试用例

**Status:** pending
**Dependencies:** 6.1

编写集成测试用例，覆盖发送邮箱验证邮件API的触发、验证链接的生成，以及邮箱验证API在成功、Token过期、Token无效等场景下的行为。预期这些测试最初会失败。

**Details:**

在`backend/tests/integration/test_auth_api.py`中创建测试方法，模拟用户请求发送验证邮件，检查响应和数据库状态。模拟用户点击验证链接，测试有效和无效Token的验证流程。

### 6.2. 实现发送邮箱验证邮件API

**Status:** pending
**Dependencies:** 6.1, 6.1

在`backend/apps/users/views.py`中实现`POST /api/auth/email/verify/send/`视图，负责生成唯一的验证Token，将其存储到`EmailVerification`表，并触发Celery任务异步发送包含验证链接的邮件。

**Details:**

创建一个序列化器用于接收请求。在视图中，为当前认证用户生成一个加密的、有时效性的Token。将Token和用户邮箱保存到`EmailVerification`模型实例中。调用一个Celery任务来发送邮件。

### 6.3. 配置Celery异步邮件发送任务和邮件模板

**Status:** pending
**Dependencies:** 6.2

定义Celery任务来处理异步邮件发送逻辑，并创建用于邮箱验证的邮件模板。

**Details:**

在`backend/apps/users/tasks.py`中定义`send_verification_email` Celery任务。任务应接收用户邮箱和验证链接作为参数。创建`email_verification.html`或`email_verification.txt`邮件模板，包含动态生成的验证链接。配置Django的邮件后端和Celery。

### 6.4. 实现邮箱验证API

**Status:** pending
**Dependencies:** 6.1, 6.1, 6.2

在`backend/apps/users/views.py`中实现`GET /api/auth/email/verify/{token}/`视图，负责接收并验证URL中的Token。如果Token有效且未过期，则更新用户的`is_email_verified`状态为True，并标记`EmailVerification`记录为已验证。

**Details:**

视图应从URL捕获`token`参数。查询`EmailVerification`表以查找匹配的Token。验证Token的有效性（未过期、未被使用）。如果验证成功，更新相关`User`模型的`is_email_verified`字段和`email_verified_at`字段，并更新`EmailVerification`记录的`verified_at`字段。处理Token无效或过期的情况，返回相应的错误响应。

### 6.5. 优化邮件模板、Celery任务和API错误处理

**Status:** pending
**Dependencies:** 6.2, 6.3, 6.4

对已实现的邮件模板、Celery任务定义和两个邮箱验证API的错误处理进行审查和优化，确保代码的健壮性、可读性和用户体验。

**Details:**

检查邮件模板的国际化和可读性。优化Celery任务的重试机制、错误日志记录。统一API的错误响应格式，处理如Token不存在、Token过期、Token已被使用等边界情况。确保所有异常都被妥善捕获和处理。
