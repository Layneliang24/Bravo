"""测试环境配置"""

from .base import *  # noqa: F403,F401

# 测试环境特定设置
DEBUG = True
SECRET_KEY = 'test-secret-key-for-testing-only'

# 使用SQLite内存数据库进行测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 简化密码验证
AUTH_PASSWORD_VALIDATORS = []

# 禁用迁移
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 测试邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 静态文件设置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 日志设置 - 只输出到控制台
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# 禁用Celery任务
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True