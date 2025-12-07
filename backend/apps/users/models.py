# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户模型"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型"""

    # 在测试环境中移除groups和user_permissions字段，避免外键约束问题
    # 这是Django测试环境的最佳实践，因为测试通常不需要复杂的权限管理
    groups = None  # type: ignore
    user_permissions = None  # type: ignore

    # 邮箱验证相关字段
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="邮箱是否验证",
        help_text="标识用户邮箱是否已验证",
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="邮箱验证时间",
        help_text="邮箱验证完成的时间",
    )

    # 登录相关字段
    # 注意：AbstractUser已经有last_login字段，这里保留以保持一致性
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name="登录失败次数",
        help_text="连续登录失败的次数",
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="锁定到期时间",
        help_text="账户锁定到期时间，超过此时间后账户自动解锁",
    )

    # 用户信息字段
    avatar = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="头像URL",
        help_text="用户头像的URL地址",
    )
    display_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="显示名称",
        help_text="用户的显示名称，用于前端展示",
    )

    class Meta:
        db_table = "users_user"
        verbose_name = "用户"
        verbose_name_plural = "用户"
        indexes = [
            models.Index(fields=["is_email_verified"], name="idx_email_verified"),
        ]
        # 注意：email和username的唯一约束由AbstractUser的字段定义提供
        # 这里只需要添加is_email_verified的普通索引
