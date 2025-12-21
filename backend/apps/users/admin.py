# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""Django管理后台配置"""

from apps.users.models import EmailVerification, PasswordReset, User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""

    list_display = [
        "id",
        "username",
        "email",
        "display_name",
        "is_email_verified",
        "email_verified_at",
        "is_active",
        "is_staff",
        "date_joined",
    ]
    list_filter = [
        "is_email_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]
    search_fields = ["username", "email", "display_name"]
    readonly_fields = ["date_joined", "last_login", "email_verified_at"]
    ordering = ["-date_joined"]
    # 移除groups和user_permissions（测试环境中这些字段被移除了）
    filter_horizontal = []

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("个人信息", {"fields": ("email", "display_name", "avatar")}),
        (
            "邮箱验证",
            {
                "fields": (
                    "is_email_verified",
                    "email_verified_at",
                )
            },
        ),
        (
            "权限",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        ("重要日期", {"fields": ("last_login", "date_joined")}),
    )

    actions = ["mark_email_verified", "delete_unverified_users"]

    @admin.action(description="标记选中用户邮箱为已验证")
    def mark_email_verified(self, request, queryset):
        """批量标记用户邮箱为已验证"""
        from django.utils import timezone

        count = 0
        for user in queryset:
            if not user.is_email_verified:
                user.is_email_verified = True
                user.email_verified_at = timezone.now()
                user.save()
                count += 1
        self.message_user(request, f"成功标记 {count} 个用户的邮箱为已验证")

    @admin.action(description="删除未验证的用户（谨慎使用）")
    def delete_unverified_users(self, request, queryset):
        """删除未验证邮箱的用户"""
        unverified = queryset.filter(is_email_verified=False)
        count = unverified.count()
        unverified.delete()
        self.message_user(
            request,
            f"成功删除 {count} 个未验证邮箱的用户",
        )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """邮箱验证管理后台"""

    list_display = [
        "id",
        "user_link",
        "email",
        "token_short",
        "is_verified",
        "is_expired",
        "expires_at",
        "verified_at",
        "created_at",
    ]
    list_filter = [
        "verified_at",
        "created_at",
        "expires_at",
    ]
    search_fields = ["email", "token", "user__username", "user__email"]
    readonly_fields = ["created_at", "token", "expires_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "user",
                    "email",
                    "token",
                )
            },
        ),
        (
            "验证状态",
            {
                "fields": (
                    "expires_at",
                    "verified_at",
                    "created_at",
                )
            },
        ),
    )

    def user_link(self, obj):
        """显示用户链接"""
        if obj.user:
            url = f"/admin/users/user/{obj.user.id}/change/"
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.user.username,
                obj.user.email,
            )
        return "-"

    user_link.short_description = "用户"  # type: ignore[attr-defined]

    def token_short(self, obj):
        """显示token的前8位"""
        if obj.token:
            return f"{obj.token[:8]}..."
        return "-"

    token_short.short_description = "Token"  # type: ignore[attr-defined]

    def is_verified(self, obj):
        """显示是否已验证"""
        if obj.is_verified():
            return format_html('<span style="color: green;">✓ 已验证</span>')
        return format_html('<span style="color: red;">✗ 未验证</span>')

    is_verified.short_description = "验证状态"  # type: ignore[attr-defined]
    is_verified.boolean = True  # type: ignore[attr-defined]

    def is_expired(self, obj):
        """显示是否过期"""
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ 已过期</span>')
        return format_html('<span style="color: green;">✓ 有效</span>')

    is_expired.short_description = "过期状态"  # type: ignore[attr-defined]
    is_expired.boolean = True  # type: ignore[attr-defined]

    actions = ["resend_verification_email", "delete_expired_verifications"]

    @admin.action(description="重新发送验证邮件")
    def resend_verification_email(self, request, queryset):
        """重新发送验证邮件"""
        from apps.users.tasks import send_email_verification

        count = 0
        for verification in queryset.filter(verified_at__isnull=True):
            if not verification.is_expired():
                send_email_verification.delay(
                    user_id=verification.user.id,
                    email=verification.email,
                    token=verification.token,
                )
                count += 1
        self.message_user(request, f"成功为 {count} 个验证记录重新发送邮件")

    @admin.action(description="删除过期的验证记录")
    def delete_expired_verifications(self, request, queryset):
        """删除过期的验证记录"""
        from django.utils import timezone

        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(request, f"成功删除 {count} 个过期的验证记录")


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    """密码重置管理后台"""

    list_display = [
        "id",
        "user_link",
        "user_email",
        "token_short",
        "is_used",
        "is_expired",
        "expires_at",
        "used_at",
        "created_at",
    ]
    list_filter = [
        "used_at",
        "created_at",
        "expires_at",
    ]
    search_fields = ["email", "token", "user__username", "user__email"]
    readonly_fields = ["created_at", "token", "expires_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def user_link(self, obj):
        """显示用户链接"""
        if obj.user:
            url = f"/admin/users/user/{obj.user.id}/change/"
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.user.username,
                obj.user.email,
            )
        return "-"

    user_link.short_description = "用户"  # type: ignore[attr-defined]

    def user_email(self, obj):
        """显示用户邮箱"""
        if obj.user:
            return obj.user.email
        return "-"

    user_email.short_description = "用户邮箱"  # type: ignore[attr-defined]

    def token_short(self, obj):
        """显示token的前8位"""
        if obj.token:
            return f"{obj.token[:8]}..."
        return "-"

    token_short.short_description = "Token"  # type: ignore[attr-defined]

    def is_used(self, obj):
        """显示是否已使用"""
        if obj.is_used():
            return format_html('<span style="color: green;">✓ 已使用</span>')
        return format_html('<span style="color: red;">✗ 未使用</span>')

    is_used.short_description = "使用状态"  # type: ignore[attr-defined]
    is_used.boolean = True  # type: ignore[attr-defined]

    def is_expired(self, obj):
        """显示是否过期"""
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ 已过期</span>')
        return format_html('<span style="color: green;">✓ 有效</span>')

    is_expired.short_description = "过期状态"  # type: ignore[attr-defined]
    is_expired.boolean = True  # type: ignore[attr-defined]


# 设置管理后台标题
admin.site.site_header = "Bravo 管理后台"
admin.site.site_title = "Bravo Admin"
admin.site.index_title = "欢迎使用Bravo管理后台"
