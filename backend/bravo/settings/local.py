"""
本地开发环境设置模板
"""

from .base import (
    BASE_DIR,
    INSTALLED_APPS,
    MIDDLEWARE,
    LOGGING,
)

# 调试模式
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bravo_local",
        "USER": "bravo_user",
        "PASSWORD": "bravo_password",
        "HOST": "mysql",
        "PORT": "3306",
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

# 邮件配置
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 静态文件配置
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 媒体文件配置
MEDIA_ROOT = BASE_DIR / "media"

# 日志配置
LOGGING["handlers"]["file"]["level"] = "DEBUG"
LOGGING["root"]["level"] = "DEBUG"

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
