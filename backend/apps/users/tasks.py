# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户相关Celery任务"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email_verification(user_id, email, token):
    """
    发送邮箱验证邮件

    Args:
        user_id: 用户ID
        email: 用户邮箱
        token: 验证令牌
    """
    # 构建验证链接（使用后端API URL）
    # 注意：这里使用后端API URL，前端会调用这个API
    backend_domain = getattr(settings, "BACKEND_DOMAIN", "http://localhost:8000")
    verification_url = f"{backend_domain}/api/auth/email/verify/{token}/"

    # 邮件主题
    subject = "请验证您的邮箱"

    # 邮件内容（纯文本）
    message = f"""
    您好！

    感谢您注册我们的服务。请点击以下链接验证您的邮箱：

    {verification_url}

    此链接将在24小时内有效。

    如果您没有注册此账户，请忽略此邮件。

    此致
    敬礼
    """

    # 获取发件人邮箱（如果未设置则使用默认值）
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@bravo.com")

    # 发送邮件
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=False,
    )
