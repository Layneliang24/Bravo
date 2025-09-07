from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""

    email = models.EmailField(unique=True, verbose_name="邮箱")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="头像"
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="个人简介")
    birth_date = models.DateField(blank=True, null=True, verbose_name="生日")
    location = models.CharField(max_length=100, blank=True, verbose_name="位置")
    website = models.URLField(blank=True, verbose_name="个人网站")

    # 用户状态
    is_verified = models.BooleanField(default=False, verbose_name="已验证")
    is_premium = models.BooleanField(default=False, verbose_name="高级用户")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    last_login_ip = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="最后登录IP"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        db_table = "users_user"

    def __str__(self):
        return self.email or self.username

    def get_full_name(self):
        """获取完整姓名"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        """获取简短姓名"""
        return self.first_name or self.username


class UserProfile(models.Model):
    """用户配置文件"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # 偏好设置
    language = models.CharField(max_length=10, default="zh-cn", verbose_name="语言")
    user_timezone = models.CharField(
        max_length=50, default="Asia/Shanghai", verbose_name="时区"
    )
    theme = models.CharField(max_length=20, default="light", verbose_name="主题")

    # 通知设置
    email_notifications = models.BooleanField(default=True, verbose_name="邮件通知")
    push_notifications = models.BooleanField(default=True, verbose_name="推送通知")

    # 隐私设置
    profile_visibility = models.CharField(
        max_length=20,
        choices=[("public", "公开"), ("friends", "仅好友"), ("private", "私密")],
        default="public",
        verbose_name="资料可见性",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "用户配置"
        verbose_name_plural = "用户配置"
        db_table = "users_profile"

    def __str__(self):
        return f"{self.user.username}的配置"


class UserActivity(models.Model):
    """用户活动记录"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=100, verbose_name="操作")
    description = models.TextField(blank=True, verbose_name="描述")
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="IP地址"
    )
    user_agent = models.TextField(blank=True, verbose_name="用户代理")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间戳")

    class Meta:
        verbose_name = "用户活动"
        verbose_name_plural = "用户活动"
        db_table = "users_activity"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} - {self.action}"
