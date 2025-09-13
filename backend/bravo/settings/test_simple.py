"""完全独立的测试环境配置 - 不依赖任何其他设置文件"""

from pathlib import Path

# 构建项目内的路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 基本设置
SECRET_KEY = "test-secret-key-for-testing-only"  # nosec
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 应用定义
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "health_check",
    "health_check.db",
]

LOCAL_APPS = [
    "apps.users",
    "apps.common",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bravo.urls"

# 模板
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "bravo.wsgi.application"

# 数据库 - 使用MySQL数据库（与开发环境保持一致）

# 强制覆盖数据库配置，避免继承base.py中的localhost配置
print("🔧 强制设置数据库配置，避免socket连接问题")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bravo_test",
        "USER": "bravo_user",
        "PASSWORD": "bravo_password",
        "HOST": "127.0.0.1",  # 必须IP，不能localhost，否则Django会去找unix socket
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
print(
    f"🔧 数据库配置: HOST={DATABASES['default']['HOST']}, PORT={DATABASES['default']['PORT']}"
)

# 密码验证 - 简化
AUTH_PASSWORD_VALIDATORS: list = []

# 国际化
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# 媒体文件
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 默认主键字段类型
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK: dict = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
}

# 禁用缓存
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# 禁用迁移
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# 禁用迁移 - CI环境使用测试数据库自动创建
MIGRATION_MODULES = DisableMigrations()

# 测试邮件后端
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

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
