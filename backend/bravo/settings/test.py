"""测试环境配置"""

from pathlib import Path

# 基础目录设置
BASE_DIR = Path(__file__).resolve().parent.parent.parent

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
    "apps.users",
    "apps.common",
]

# 中间件 - 简化版本
MIDDLEWARE = [
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
import os

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

# 禁用缓存
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# 简化密码验证器
AUTH_PASSWORD_VALIDATORS: list = []

# 自定义用户模型
AUTH_USER_MODEL = "users.User"

# 测试环境不需要CORS配置


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

# 测试邮件后端
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

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
