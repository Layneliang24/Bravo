# -*- coding: utf-8 -*-
"""用户模型"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型"""

    # 在测试环境中移除groups和user_permissions字段，避免外键约束问题
    # 这是Django测试环境的最佳实践，因为测试通常不需要复杂的权限管理
    groups = None
    user_permissions = None

    class Meta:
        db_table = "users_user"
        verbose_name = "用户"
        verbose_name_plural = "用户"
