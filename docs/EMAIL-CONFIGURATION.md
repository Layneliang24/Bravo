# 邮件配置说明

> **问题**: 注册后没有收到验证邮件
> **原因**: 当前使用测试环境配置，邮件后端为内存后端，不会真正发送邮件

---

## 🔍 当前配置状态

### 开发环境配置

**后端服务** (`docker-compose.yml`):

- 使用: `bravo.settings.test`
- 邮件后端: `django.core.mail.backends.locmem.EmailBackend` (内存后端)
- **结果**: 邮件不会真正发送，只存储在内存中

**Celery服务** (`docker-compose.yml`):

- 使用: `bravo.settings.local`
- 邮件后端: `django.core.mail.backends.console.EmailBackend` (控制台后端)
- **结果**: 邮件会打印到Celery容器的控制台日志中

---

## 📧 配置真实邮件发送

### 方法1: 使用Gmail SMTP（推荐用于开发测试）

#### 1. 获取Gmail应用密码

1. 登录Gmail账户
2. 进入 [Google账户设置](https://myaccount.google.com/)
3. 选择"安全性" → "两步验证"（如果未启用，先启用）
4. 选择"应用密码"
5. 生成新的应用密码（选择"邮件"和"其他设备"）
6. 复制生成的16位密码

#### 2. 配置环境变量

在 `docker-compose.yml` 的 `backend` 和 `celery` 服务中添加：

```yaml
backend:
  environment:
    # ... 其他配置 ...
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=your-app-password # Gmail应用密码
    - DEFAULT_FROM_EMAIL=your-email@gmail.com

celery:
  environment:
    # ... 其他配置 ...
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=your-app-password
    - DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### 3. 修改settings文件

**修改 `backend/bravo/settings/test.py`**:

```python
# 邮件配置
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.locmem.EmailBackend"  # 默认使用内存后端
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")
```

**修改 `backend/bravo/settings/local.py`**:

```python
# 邮件配置
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"  # 默认使用控制台后端
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@bravo.com")
```

#### 4. 重启服务

```bash
docker-compose restart backend celery
```

---

### 方法2: 使用其他SMTP服务

#### QQ邮箱

```yaml
environment:
  - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  - EMAIL_HOST=smtp.qq.com
  - EMAIL_PORT=587
  - EMAIL_USE_TLS=True
  - EMAIL_HOST_USER=your-email@qq.com
  - EMAIL_HOST_PASSWORD=your-authorization-code # QQ邮箱授权码
  - DEFAULT_FROM_EMAIL=your-email@qq.com
```

#### 163邮箱

```yaml
environment:
  - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  - EMAIL_HOST=smtp.163.com
  - EMAIL_PORT=465
  - EMAIL_USE_SSL=True
  - EMAIL_HOST_USER=your-email@163.com
  - EMAIL_HOST_PASSWORD=your-authorization-code
  - DEFAULT_FROM_EMAIL=your-email@163.com
```

#### 企业邮箱（如阿里云企业邮箱）

```yaml
environment:
  - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  - EMAIL_HOST=smtp.mxhichina.com # 根据服务商调整
  - EMAIL_PORT=465
  - EMAIL_USE_SSL=True
  - EMAIL_HOST_USER=your-email@yourdomain.com
  - EMAIL_HOST_PASSWORD=your-password
  - DEFAULT_FROM_EMAIL=your-email@yourdomain.com
```

---

### 方法3: 开发环境使用控制台后端（查看邮件内容）

如果只是想查看邮件内容而不真正发送，可以：

1. **查看Celery日志**:

   ```bash
   docker-compose logs celery -f
   ```

2. **邮件会打印在控制台**，格式类似：

   ```
   Content-Type: text/plain; charset="utf-8"
   From: noreply@bravo.com
   To: user@example.com
   Subject: 请验证您的邮箱

   请点击以下链接验证您的邮箱：
   http://localhost:8000/api/auth/email/verify/{token}/
   ```

---

## 🔧 快速配置步骤

### 使用Gmail（推荐）

1. **获取Gmail应用密码**（见上文）

2. **修改 `docker-compose.yml`**:

```yaml
backend:
  environment:
    # ... 现有配置 ...
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx # 16位应用密码
    - DEFAULT_FROM_EMAIL=your-email@gmail.com

celery:
  environment:
    # ... 现有配置 ...
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
    - DEFAULT_FROM_EMAIL=your-email@gmail.com
```

3. **更新settings文件支持环境变量**（见上文）

4. **重启服务**:

   ```bash
   docker-compose restart backend celery
   ```

5. **测试邮件发送**:
   - 注册新用户
   - 检查邮箱收件箱（包括垃圾邮件文件夹）
   - 查看Celery日志确认任务执行: `docker-compose logs celery -f`

---

## 🐛 故障排查

### 1. 检查邮件配置

```bash
docker-compose exec backend python manage.py shell -c "
from django.conf import settings
print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_HOST:', getattr(settings, 'EMAIL_HOST', 'Not set'))
print('EMAIL_PORT:', getattr(settings, 'EMAIL_PORT', 'Not set'))
print('EMAIL_HOST_USER:', getattr(settings, 'EMAIL_HOST_USER', 'Not set'))
print('DEFAULT_FROM_EMAIL:', getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set'))
"
```

### 2. 检查Celery任务执行

```bash
# 查看Celery日志
docker-compose logs celery -f

# 查看Celery任务状态
docker-compose exec celery celery -A bravo inspect active
```

### 3. 检查邮件发送错误

```bash
# 查看后端日志
docker-compose logs backend | grep -i "email\|mail\|error"

# 查看Celery日志
docker-compose logs celery | grep -i "email\|mail\|error"
```

### 4. 常见错误

**错误1: `SMTPAuthenticationError`**

- **原因**: 用户名或密码错误
- **解决**: 检查 `EMAIL_HOST_USER` 和 `EMAIL_HOST_PASSWORD` 是否正确

**错误2: `SMTPServerDisconnected`**

- **原因**: SMTP服务器连接失败
- **解决**: 检查 `EMAIL_HOST` 和 `EMAIL_PORT` 是否正确

**错误3: 邮件进入垃圾箱**

- **原因**: 发件人邮箱未验证或SPF/DKIM未配置
- **解决**: 使用已验证的邮箱，或配置SPF/DKIM记录

---

## 📝 注意事项

1. **安全性**: 不要在代码中硬编码密码，使用环境变量
2. **开发环境**: 可以使用控制台后端查看邮件内容
3. **生产环境**: 必须使用真实的SMTP服务器
4. **Gmail限制**: Gmail有每日发送限制（约500封/天），生产环境建议使用专业邮件服务

---

## 🔗 相关文件

- `backend/bravo/settings/test.py` - 测试环境配置
- `backend/bravo/settings/local.py` - 本地开发配置
- `backend/bravo/settings/production.py` - 生产环境配置
- `backend/apps/users/tasks.py` - 邮件发送Celery任务
- `docker-compose.yml` - Docker环境变量配置
