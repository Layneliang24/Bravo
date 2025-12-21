"""测试环境配置"""

import os
from datetime import timedelta
from pathlib import Path

# 基础目录设置
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 前端和后端域名配置（用于邮件链接等）
FRONTEND_DOMAIN = os.environ.get("FRONTEND_DOMAIN", "http://localhost:3000")
BACKEND_DOMAIN = os.environ.get("BACKEND_DOMAIN", "http://localhost:8000")

# 测试环境特定设置
DEBUG = True
SECRET_KEY = "test-secret-key-for-testing-only"  # nosec
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1", "*"]

# Django核心设置
ROOT_URLCONF = "bravo.urls_test"
WSGI_APPLICATION = "bravo.wsgi.application"

# 应用设置 - 确保Django核心应用在自定义应用之前
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",  # CORS支持（浏览器访问需要）
    "rest_framework",
    "drf_spectacular",  # API文档生成
    "apps.users",
    "apps.common",
]

# 中间件 - 简化版本
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS必须在最前面
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 模板设置
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 国际化
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# 静态文件和媒体文件
STATIC_URL = "/static/"
STATICFILES_DIRS = []  # 暂时为空，避免目录不存在警告
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 使用MySQL数据库进行测试（与开发环境保持一致）

# 强制覆盖数据库配置，避免继承base.py中的localhost配置
print("🔧 强制设置数据库配置，避免socket连接问题")

# 根据环境自动选择数据库主机
# GitHub Actions CI环境使用127.0.0.1，本地环境也使用127.0.0.1，Docker环境使用mysql
db_host = os.environ.get("DB_HOST", "127.0.0.1")
db_user = os.environ.get("DB_USER", "bravo_user")
db_password = os.environ.get("DB_PASSWORD", "bravo_password")
db_name = os.environ.get("DB_NAME", "bravo_test")
db_port = os.environ.get("DB_PORT", "3306")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": db_name,
        "USER": db_user,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES', foreign_key_checks=0",
        },
    }
}
print(
    f"🔧 数据库配置: HOST={DATABASES['default']['HOST']}, PORT={DATABASES['default']['PORT']}, CI={os.environ.get('CI', 'False')}"
)

# Redis缓存配置（测试环境也需要真实的缓存来存储验证码）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # 使用容器名称redis
        "KEY_PREFIX": "bravo_test",
        "TIMEOUT": 300,  # 默认5分钟
    }
}

# 简化密码验证器
AUTH_PASSWORD_VALIDATORS: list = []

# 自定义用户模型
AUTH_USER_MODEL = "users.User"

# CORS配置 - 浏览器访问需要（测试在容器内不经过浏览器，但实际部署时浏览器需要）
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# 测试数据库配置 - 使用事务回滚，避免外键约束问题
DATABASES["default"].update(
    {
        "TEST": {
            "NAME": "bravo_test",
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_unicode_ci",
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES', foreign_key_checks=0",
            },
        }
    }
)

# 使用Django的迁移系统，确保表创建顺序正确
# 不禁用迁移，让Django正确处理外键依赖关系

# 邮件配置（支持通过环境变量覆盖）
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.locmem.EmailBackend",  # 默认使用内存后端（测试环境）
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", os.environ.get("EMAIL_USER", ""))
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD", os.environ.get("EMAIL_PASSWORD", "")
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")

# 静态文件设置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 日志设置 - 只输出到控制台
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# 禁用Celery任务
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# REST Framework配置（测试环境）
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# JWT配置（测试环境）
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# drf-spectacular (OpenAPI/Swagger) 配置
SPECTACULAR_SETTINGS = {
    "TITLE": "Bravo API 文档 (测试环境)",
    "DESCRIPTION": "Bravo项目API文档，基于OpenAPI 3.0规范",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
}

# REST Framework配置（测试环境） - 添加schema类
REST_FRAMEWORK.update(
    {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }
)

# 验证码测试环境配置（E2E测试专用）
# 万能验证码：在测试环境下，如果输入的验证码是此值，则直接通过验证
# 这解决了E2E测试中验证码的随机性问题，避免"调试地狱"
# 注意：验证码是4位的，所以万能验证码也必须是4位
TEST_CAPTCHA_BYPASS = os.environ.get("TEST_CAPTCHA_BYPASS", "6666")
