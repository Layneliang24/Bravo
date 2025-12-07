# Task ID: 2

**Title:** 后端：验证码生成与API实现

**Status:** pending

**Dependencies:** 1

**Priority:** high

**Description:** 实现图形验证码的生成、Redis存储、过期管理以及获取和刷新验证码的API接口。

**Details:**

1. **红（Red）**：编写测试用例，验证验证码生成逻辑、Redis存储、过期机制以及API响应格式，预期测试失败。2. **绿（Green）**：在`backend/apps/users/utils.py`中实现验证码生成逻辑，使用Pillow生成4位数字+字母混合验证码，添加干扰线和噪点，Base64编码图片。在Redis中存储验证码答案，Key格式为`captcha:{session_id}`，设置5分钟过期。在`backend/apps/users/views.py`中创建`GET /api/auth/captcha/`接口用于获取验证码（返回`captcha_id`, `captcha_image`, `expires_in`）和`POST /api/auth/captcha/refresh/`接口用于刷新验证码。3. **重构（Refactor）**：优化验证码生成算法和Redis操作。

**Test Strategy:**

编写`backend/tests/unit/test_captcha.py`单元测试，测试验证码生成是否符合预期、Redis存储和过期是否正常、验证码验证逻辑是否正确。编写集成测试，验证`/api/auth/captcha/`和`/api/auth/captcha/refresh/`接口的响应数据结构和功能。

## Subtasks

### 2.1. 编写验证码模块的单元测试

**Status:** pending
**Dependencies:** None

为验证码生成逻辑、Redis存储和过期机制以及API响应格式编写初步的单元测试，预期测试失败。

**Details:**

在`backend/tests/unit/test_captcha.py`中创建测试文件。编写测试用例，验证验证码图片生成是否符合预期（例如，长度、字符类型），Redis存储和检索功能，以及验证码过期机制。同时，为API接口的响应结构和数据类型编写测试，确保它们在后续实现中能被正确验证。

### 2.2. 实现验证码生成工具函数

**Status:** pending
**Dependencies:** 2.1

在`backend/apps/users/utils.py`中实现图形验证码的生成逻辑，包括字符生成、图片绘制和Base64编码。

**Details:**

使用Pillow库在`backend/apps/users/utils.py`中实现一个函数，该函数能生成一个4位数字+字母混合的随机验证码字符串。同时，利用Pillow绘制包含干扰线和噪点的验证码图片，并将图片Base64编码为字符串返回。该函数应返回验证码文本和Base64编码的图片。

### 2.3. 实现验证码Redis存储与过期管理

**Status:** pending
**Dependencies:** 2.1, 2.2

实现将生成的验证码答案存储到Redis中，并设置5分钟的过期时间。

**Details:**

在`backend/apps/users/utils.py`或独立的Redis服务模块中，实现将验证码答案存储到Redis的函数。Redis Key的格式应为`captcha:{session_id}`，其中`session_id`是一个唯一的标识符。设置验证码在Redis中的过期时间为5分钟。同时，实现从Redis获取和删除验证码答案的函数。

### 2.4. 实现获取验证码API (`GET /api/auth/captcha/`)

**Status:** pending
**Dependencies:** 2.1, 2.2, 2.3

在`backend/apps/users/views.py`中创建`GET /api/auth/captcha/`接口，用于生成、存储并返回新的验证码。

**Details:**

在`backend/apps/users/views.py`中实现一个视图函数，处理`GET /api/auth/captcha/`请求。该接口应调用验证码生成工具函数生成新的验证码，将其答案存储到Redis，并返回包含`captcha_id`（用于标识本次验证码）、`captcha_image`（Base64编码的图片）和`expires_in`（过期时间，秒）的JSON响应。

### 2.5. 实现刷新验证码API (`POST /api/auth/captcha/refresh/`) 并进行初步重构

**Status:** pending
**Dependencies:** 2.1, 2.2, 2.3, 2.4

在`backend/apps/users/views.py`中创建`POST /api/auth/captcha/refresh/`接口，用于刷新现有验证码，并对已实现的代码进行初步优化。

**Details:**

在`backend/apps/users/views.py`中实现一个视图函数，处理`POST /api/auth/captcha/refresh/`请求。该接口应接收旧的`captcha_id`（可选），生成新的验证码，更新Redis中的存储，并返回新的`captcha_id`、`captcha_image`和`expires_in`。同时，对子任务2、3、4中实现的代码进行初步的代码审查和重构，确保代码清晰、可读性高，并遵循最佳实践，例如，提取重复逻辑到辅助函数中。
