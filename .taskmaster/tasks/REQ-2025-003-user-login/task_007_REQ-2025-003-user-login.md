# Task ID: 7

**Title:** 后端：密码找回API与异步邮件发送

**Status:** pending

**Dependencies:** 1, 2, 5

**Priority:** high

**Description:** 实现发送密码重置邮件 (`POST /api/auth/password/reset/send/`) 和重置密码 (`POST /api/auth/password/reset/`) 的API接口，并集成Celery进行异步邮件发送。

**Details:**

1. **红（Red）**：编写测试用例，验证发送重置邮件API的触发、重置链接的生成、密码重置成功和失败（如token过期、无效）的场景，预期测试失败。2. **绿（Green）**：在`backend/apps/users/views.py`中实现`POST /api/auth/password/reset/send/`视图，验证邮箱是否存在，生成唯一的重置Token，存储到`PasswordReset`表，并使用Celery异步发送包含重置链接的邮件，该接口需验证码保护。实现`POST /api/auth/password/reset/`视图，验证Token的有效性和未使用状态，更新用户密码，并标记`PasswordReset`记录为已使用。3. **重构（Refactor）**：优化邮件模板、Celery任务定义和错误处理。

**Test Strategy:**

编写`backend/tests/integration/test_password_reset.py`集成测试，测试发送重置邮件API是否触发Celery任务，验证链接是否正确生成。测试密码重置API，验证有效Token和过期/无效Token的响应，以及密码更新是否成功。

## Subtasks

### 7.1. 编写密码找回API集成测试用例

**Status:** pending
**Dependencies:** None

编写集成测试用例，覆盖发送密码重置邮件API (`POST /api/auth/password/reset/send/`) 和重置密码API (`POST /api/auth/password/reset/`) 的各种场景，包括成功发送邮件、重置链接生成、密码成功重置、Token过期或无效、邮箱不存在等。预期这些测试在API未实现时会失败。

**Details:**

在`backend/tests/integration/test_password_reset.py`中创建测试文件，使用Django测试客户端模拟API请求。测试`POST /api/auth/password/reset/send/`接口，验证其响应和是否触发Celery任务。测试`POST /api/auth/password/reset/`接口，验证有效和无效Token的响应，以及密码更新的正确性。

### 7.2. 实现密码重置Token模型与异步邮件发送服务

**Status:** pending
**Dependencies:** None

定义`PasswordReset`模型用于存储密码重置Token及其状态。创建Celery任务，负责异步发送包含密码重置链接的电子邮件。

**Details:**

在`backend/apps/users/models.py`中创建`PasswordReset`模型，包含`user`外键、`token`字段、`expires_at`字段、`is_used`布尔字段和`created_at`字段。在`backend/apps/users/tasks.py`中定义一个Celery任务，接收用户邮箱和重置链接，使用Django的`send_mail`或类似功能发送邮件。

### 7.3. 实现发送密码重置邮件API

**Status:** pending
**Dependencies:** 7.1, 7.2

实现`POST /api/auth/password/reset/send/`接口。该接口应验证请求中的邮箱是否存在，生成唯一的密码重置Token，将其存储到`PasswordReset`表中，并调用Celery任务异步发送包含重置链接的邮件。此接口需集成验证码保护。

**Details:**

在`backend/apps/users/views.py`中创建`PasswordResetSendView`。使用序列化器验证邮箱和验证码。如果邮箱存在，生成一个安全的、有时效性的Token，保存到`PasswordReset`模型实例中。构建重置链接（例如：`frontend_url/reset-password?token={token}`）。调用之前定义的Celery任务发送邮件。

### 7.4. 实现重置密码API

**Status:** pending
**Dependencies:** 7.1, 7.2, 7.3

实现`POST /api/auth/password/reset/`接口。该接口负责验证提供的重置Token的有效性（未过期且未使用），更新用户的密码，并标记对应的`PasswordReset`记录为已使用。

**Details:**

在`backend/apps/users/views.py`中创建`PasswordResetConfirmView`。使用序列化器验证Token和新密码。查询`PasswordReset`表，验证Token是否存在、未过期且未使用。如果验证通过，更新对应用户的密码，并使用Django的`set_password`方法哈希新密码。将`PasswordReset`记录的`is_used`字段设置为`True`。

### 7.5. 优化邮件模板、Celery任务与错误处理

**Status:** pending
**Dependencies:** 7.3, 7.4

优化密码重置邮件的模板，使其更具用户友好性和专业性。审查并优化Celery任务的定义，确保其健壮性和可维护性。统一并完善密码找回相关API的错误处理机制，提供清晰的错误信息。

**Details:**

创建或修改邮件模板文件（例如，HTML模板），包含品牌信息和清晰的重置说明。检查Celery任务的重试机制、错误日志记录和任务参数传递。审查`PasswordResetSendView`和`PasswordResetConfirmView`中的异常捕获和响应，确保返回一致且有意义的错误码和消息。
