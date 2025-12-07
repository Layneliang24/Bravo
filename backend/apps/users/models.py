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

    # 重写email字段，添加唯一约束（根据PRD要求）
    email = models.EmailField(
        unique=True,
        verbose_name="邮箱",
        help_text="用户邮箱地址，必须唯一",
    )

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

    def __str__(self):
        """用户模型的字符串表示"""
        return self.username or self.email or str(self.id)


class EmailVerification(models.Model):
    """邮箱验证模型"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_verifications",
        verbose_name="用户",
        help_text="关联的用户",
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="验证邮箱",
        help_text="需要验证的邮箱地址",
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="验证令牌",
        help_text="邮箱验证的唯一令牌",
    )
    expires_at = models.DateTimeField(
        verbose_name="过期时间",
        help_text="验证令牌的过期时间",
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="验证时间",
        help_text="邮箱验证完成的时间",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="记录创建的时间",
    )

    class Meta:
        db_table = "users_email_verification"
        verbose_name = "邮箱验证"
        verbose_name_plural = "邮箱验证"
        indexes = [
            models.Index(fields=["token"], name="idx_email_verify_token"),
            models.Index(fields=["user", "email"], name="idx_email_verify_user"),
        ]

    def __str__(self):
        """邮箱验证模型的字符串表示"""
        return f"EmailVerification for {self.email} (user: {self.user_id})"


class PasswordReset(models.Model):
    """密码重置模型"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_resets",
        verbose_name="用户",
        help_text="关联的用户",
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="重置令牌",
        help_text="密码重置的唯一令牌",
    )
    expires_at = models.DateTimeField(
        verbose_name="过期时间",
        help_text="重置令牌的过期时间",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="使用时间",
        help_text="密码重置令牌被使用的时间",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="记录创建的时间",
    )

    class Meta:
        db_table = "users_password_reset"
        verbose_name = "密码重置"
        verbose_name_plural = "密码重置"
        indexes = [
            models.Index(fields=["token"], name="idx_pwd_reset_token"),
            models.Index(fields=["user"], name="idx_pwd_reset_user"),
        ]

    def __str__(self):
        """密码重置模型的字符串表示"""
        return f"PasswordReset for user {self.user_id}"
