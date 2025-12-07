# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户相关Celery任务"""

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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

    # 渲染HTML模板
    html_content = render_to_string(
        "users/emails/email_verification.html",
        {"verification_url": verification_url},
    )

    # 渲染纯文本模板
    text_content = render_to_string(
        "users/emails/email_verification.txt",
        {"verification_url": verification_url},
    )

    # 获取发件人邮箱（如果未设置则使用默认值）
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@bravo.com")

    # 创建邮件消息（支持HTML和纯文本）
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # 纯文本版本
        from_email=from_email,
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")  # HTML版本

    # 发送邮件
    msg.send(fail_silently=False)
