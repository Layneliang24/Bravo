"""本地开发环境设置模板"""

import os
from typing import Any

from decouple import config

from .base import *

# 数据库配置优化
# 确保使用TCP连接而不是socket连接

# 调试模式
DEBUG = True

# 允许的主机 - 仅允许本地访问以提高安全性
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# 数据库配置 - 使用SQLite进行本地开发
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME", default="bravo_local"),
        "USER": config("DB_USER", default="bravo_user"),
        "PASSWORD": config("DB_PASSWORD", default="bravo_password"),
        "HOST": config("DB_HOST", default="mysql"),
        "PORT": config("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

# 开发工具
if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
        "django_extensions",
        "silk",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "silk.middleware.SilkyMiddleware",
    ]

    # 调试工具栏配置
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

    # Silk 配置
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True

# 邮件配置（支持通过环境变量覆盖）
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"  # 默认使用控制台后端（开发环境）
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", os.environ.get("EMAIL_USER", ""))
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD", os.environ.get("EMAIL_PASSWORD", "")
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@bravo.com")

# 静态文件配置
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 媒体文件配置
MEDIA_ROOT = BASE_DIR / "media"

# 日志配置
logging_config: dict[str, Any] = LOGGING
logging_config["handlers"]["file"]["level"] = "DEBUG"
logging_config["root"]["level"] = "DEBUG"
LOGGING = logging_config

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 缓存配置（使用内存缓存进行开发）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery 配置（开发环境使用同步模式）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
