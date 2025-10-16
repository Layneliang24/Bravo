"""
生产环境配置
基于development.py，但增加了生产环境的安全和性能配置
"""

import os

from .base import *

# 生产环境基础配置
DEBUG = False
ALLOWED_HOSTS = [
    "8.129.16.190",  # 服务器IP
    "localhost",
    "127.0.0.1",
    # 域名配置
    "layneliang.com",  # 生产域名
    "www.layneliang.com",
    "dev.layneliang.com",  # 开发域名
]

# 安全配置
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "your-very-secret-production-key-change-this"
)

# 数据库配置 - 生产环境使用MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "bravo_production"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "root_password"),
        "HOST": os.environ.get("DB_HOST", "mysql"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Redis缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# 会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = not os.environ.get("DISABLE_SSL_REDIRECT", False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF保护
CSRF_COOKIE_SECURE = not os.environ.get("DISABLE_SSL_REDIRECT", False)
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    "https://8.129.16.190",
    "https://8.129.16.190:8443",  # Dev环境HTTPS端口
    "https://layneliang.com",  # 生产域名
    "https://www.layneliang.com",
    "https://dev.layneliang.com",  # 开发域名
    "https://dev.layneliang.com:8443",
    "http://8.129.16.190:8080",  # Dev环境HTTP端口
    "http://dev.layneliang.com:8080",
]

# HTTPS安全配置
SECURE_SSL_REDIRECT = not os.environ.get("DISABLE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# 静态文件配置
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

# 文件存储配置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/django/bravo.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "bravo": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# 邮件配置
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@yourdomain.com")

# Celery配置
CELERY_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"
CELERY_RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = True

# 性能配置
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# API限流配置
REST_FRAMEWORK.update(
    {
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {"anon": "1000/day", "user": "5000/day"},
    }
)

# 监控配置
if os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(auto_enabling_integrations=False),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

# 健康检查
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # 磁盘使用率不超过90%
    "MEMORY_MIN": 100,  # 可用内存不少于100MB
}

print("🏭 生产环境配置已加载")
