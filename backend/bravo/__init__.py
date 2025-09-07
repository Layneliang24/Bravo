# Django 项目包标识模板

# 确保celery应用在Django启动时被加载
from .celery import app as celery_app

__all__ = ("celery_app",)
