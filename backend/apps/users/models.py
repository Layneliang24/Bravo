# -*- coding: utf-8 -*-
"""用户模型"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型"""
    
    # 移除groups字段，避免外键约束问题
    groups = None
    user_permissions = None
    
    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'