# 邮件配置快速指南

> **问题**: 注册后没有收到验证邮件
> **原因**: 当前使用测试环境配置，邮件不会真正发送

---

## 🚀 快速配置（3步）

### 步骤1: 获取Gmail应用密码

1. 登录 [Google账户设置](https://myaccount.google.com/)
2. 安全性 → 两步验证（如未启用，先启用）
3. 应用密码 → 生成新密码（选择"邮件"和"其他设备"）
4. 复制16位密码（格式：`xxxx xxxx xxxx xxxx`）

### 步骤2: 修改 `docker-compose.yml`

在 `backend` 和 `celery` 服务的 `environment` 部分，取消注释并填写邮件配置：

```yaml
backend:
  environment:
    # ... 其他配置 ...
    # 取消注释以下行并填写你的Gmail信息
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx # 16位应用密码
    - DEFAULT_FROM_EMAIL=your-email@gmail.com

celery:
  environment:
    # ... 其他配置 ...
    # 取消注释以下行并填写你的Gmail信息
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    - EMAIL_HOST=smtp.gmail.com
    - EMAIL_PORT=587
    - EMAIL_USE_TLS=True
    - EMAIL_HOST_USER=your-email@gmail.com
    - EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
    - DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 步骤3: 重启服务

```bash
docker-compose restart backend celery
```

---

## ✅ 验证配置

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

应该看到：

```
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_HOST_USER: your-email@gmail.com
DEFAULT_FROM_EMAIL: your-email@gmail.com
```

### 2. 测试邮件发送

1. 注册新用户
2. 检查邮箱收件箱（包括垃圾邮件文件夹）
3. 查看Celery日志确认任务执行：

```bash
docker-compose logs celery -f
```

应该看到类似：

```
[INFO] 邮箱验证邮件发送成功: user_id=1, email=user@example.com
```

---

## 🔍 当前状态说明

### 开发环境默认配置

- **后端服务**: 使用 `locmem.EmailBackend`（内存后端）

  - 邮件不会真正发送，只存储在内存中
  - 用于测试，不会产生实际邮件

- **Celery服务**: 使用 `console.EmailBackend`（控制台后端）
  - 邮件会打印到Celery容器的控制台日志中
  - 可以查看邮件内容，但不会真正发送

### 查看邮件内容（不配置SMTP）

如果想查看邮件内容而不真正发送，可以：

```bash
# 查看Celery日志（邮件会打印在这里）
docker-compose logs celery -f
```

---

## 📧 其他邮件服务商配置

### QQ邮箱

```yaml
- EMAIL_HOST=smtp.qq.com
- EMAIL_PORT=587
- EMAIL_USE_TLS=True
- EMAIL_HOST_USER=your-email@qq.com
- EMAIL_HOST_PASSWORD=your-authorization-code # QQ邮箱授权码
```

### 163邮箱

```yaml
- EMAIL_HOST=smtp.163.com
- EMAIL_PORT=465
- EMAIL_USE_SSL=True # 注意：使用SSL而不是TLS
- EMAIL_HOST_USER=your-email@163.com
- EMAIL_HOST_PASSWORD=your-authorization-code
```

---

## 🐛 常见问题

### Q1: 配置后仍然收不到邮件？

**检查清单**:

1. ✅ 是否重启了 `backend` 和 `celery` 服务？
2. ✅ Gmail应用密码是否正确（16位，无空格）？
3. ✅ 是否检查了垃圾邮件文件夹？
4. ✅ Celery日志中是否有错误信息？

### Q2: 如何查看邮件发送错误？

```bash
# 查看Celery错误日志
docker-compose logs celery | grep -i "error\|exception\|failed"

# 查看后端错误日志
docker-compose logs backend | grep -i "email\|mail\|error"
```

### Q3: Gmail提示"不允许使用此应用登录"？

**解决**:

1. 确保已启用"两步验证"
2. 使用"应用密码"而不是Gmail账户密码
3. 应用密码格式：`xxxx xxxx xxxx xxxx`（16位，中间有空格）

---

## 📝 详细文档

更多配置选项和故障排查，请参考：

- `docs/EMAIL-CONFIGURATION.md` - 完整配置文档

---

## ⚡ 快速命令

```bash
# 重启服务
docker-compose restart backend celery

# 查看邮件配置
docker-compose exec backend python manage.py shell -c "from django.conf import settings; print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)"

# 查看Celery日志
docker-compose logs celery -f

# 测试邮件发送（在Django shell中）
docker-compose exec backend python manage.py shell
# 然后执行：
# from django.core.mail import send_mail
# send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```
