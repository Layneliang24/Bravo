# Task ID: 1

**Title:** 后端：数据库模型扩展与迁移

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** 根据PRD要求，扩展现有的User模型，并创建EmailVerification和PasswordReset模型，包含所有指定字段和索引。

**Details:**

1. **红（Red）**：编写测试用例，验证User模型新增字段、EmailVerification和PasswordReset模型的创建及其字段、索引是否符合预期，预期测试失败。2. **绿（Green）**：在`backend/apps/users/models.py`中扩展`User`模型，添加`is_email_verified`, `email_verified_at`, `last_login`, `failed_login_attempts`, `locked_until`, `avatar`, `display_name`字段。创建`EmailVerification`和`PasswordReset`模型，包含`id`, `user_id`, `email`, `token`, `expires_at`, `verified_at`/`used_at`, `created_at`字段。为`User`表的`email`, `username`, `is_email_verified`字段以及`EmailVerification`和`PasswordReset`表的`token`字段添加唯一索引。运行`makemigrations`和`migrate`。3. **重构（Refactor）**：优化模型定义，确保字段类型和约束正确。

**Test Strategy:**

编写`backend/tests/unit/test_auth_models.py`单元测试，验证User模型字段是否存在、默认值是否正确、索引是否创建。验证EmailVerification和PasswordReset模型能够被创建、字段类型和外键关系正确、唯一索引生效。

## Subtasks

### 1.1. 编写数据库模型扩展的单元测试

**Status:** pending
**Dependencies:** None

根据PRD要求，编写单元测试用例，验证User模型新增字段、EmailVerification和PasswordReset模型的创建及其字段、索引是否符合预期。预期这些测试在模型未实现时会失败。

**Details:**

在`backend/tests/unit/test_auth_models.py`中创建测试文件。编写测试用例以验证`User`模型是否包含`is_email_verified`, `email_verified_at`, `last_login`, `failed_login_attempts`, `locked_until`, `avatar`, `display_name`字段。编写测试用例以验证`EmailVerification`和`PasswordReset`模型是否存在，并包含所有指定字段（`id`, `user_id`, `email`, `token`, `expires_at`, `verified_at`/`used_at`, `created_at`）。验证`User`表的`email`, `username`, `is_email_verified`字段以及`EmailVerification`和`PasswordReset`表的`token`字段的唯一索引是否被正确定义。

### 1.2. 扩展User模型字段

**Status:** pending
**Dependencies:** 1.1

在`backend/apps/users/models.py`中扩展现有的`User`模型，添加所有指定的新字段。

**Details:**

修改`backend/apps/users/models.py`文件，在`User`模型中添加`is_email_verified` (BooleanField, default=False), `email_verified_at` (DateTimeField, nullable), `last_login` (DateTimeField, nullable), `failed_login_attempts` (IntegerField, default=0), `locked_until` (DateTimeField, nullable), `avatar` (ImageField/URLField, nullable), `display_name` (CharField, nullable)字段。确保字段类型和默认值设置正确。

### 1.3. 创建EmailVerification和PasswordReset模型

**Status:** pending
**Dependencies:** 1.2

在`backend/apps/users/models.py`中创建`EmailVerification`和`PasswordReset`两个新模型，包含所有指定字段。

**Details:**

在`backend/apps/users/models.py`中定义`EmailVerification`模型，包含`id` (UUIDField/AutoField), `user` (ForeignKey to User), `email` (EmailField), `token` (CharField), `expires_at` (DateTimeField), `verified_at` (DateTimeField, nullable), `created_at` (DateTimeField, auto_now_add=True)字段。定义`PasswordReset`模型，包含`id` (UUIDField/AutoField), `user` (ForeignKey to User), `email` (EmailField), `token` (CharField), `expires_at` (DateTimeField), `used_at` (DateTimeField, nullable), `created_at` (DateTimeField, auto_now_add=True)字段。确保外键关系正确。

### 1.4. 添加模型索引并执行数据库迁移

**Status:** pending
**Dependencies:** 1.3

为`User`、`EmailVerification`和`PasswordReset`模型中的指定字段添加唯一索引，并生成和应用数据库迁移文件。

**Details:**

在`User`模型的`Meta`类中，为`email`和`username`字段添加`unique=True`约束，并考虑为`is_email_verified`添加索引（如果需要查询优化）。在`EmailVerification`和`PasswordReset`模型的`Meta`类中，为`token`字段添加`unique=True`约束。运行`python manage.py makemigrations users`生成迁移文件，然后运行`python manage.py migrate`应用这些迁移到数据库。

### 1.5. 优化模型定义和字段约束

**Status:** pending
**Dependencies:** 1.4

对所有新创建和扩展的模型进行代码审查和优化，确保字段类型、默认值、约束和关系符合最佳实践，提高代码质量。

**Details:**

审查`User`、`EmailVerification`和`PasswordReset`模型的字段定义，确保使用了最合适的Django字段类型（例如，对于`avatar`字段，考虑使用`ImageField`并配置存储，或者`URLField`）。检查所有`null=True`和`blank=True`的设置是否合理。确保外键关系（`ForeignKey`）的`on_delete`行为正确。添加必要的`__str__`方法以提高模型的可读性。
