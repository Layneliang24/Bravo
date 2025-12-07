# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户相关Celery任务"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60秒后重试
    autoretry_for=(Exception,),  # 对所有异常自动重试
    retry_backoff=True,  # 指数退避
    retry_backoff_max=600,  # 最大退避时间600秒
    retry_jitter=True,  # 添加随机抖动避免同时重试
)
def send_email_verification(self, user_id, email, token):
    """
    发送邮箱验证邮件

    Args:
        user_id: 用户ID
        email: 用户邮箱
        token: 验证令牌

    Raises:
        Exception: 邮件发送失败时抛出异常，触发重试机制
    """
    try:
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

        # 记录成功日志
        logger.info(
            f"邮箱验证邮件发送成功: user_id={user_id}, email={email}, "
            f"retry_count={self.request.retries}"
        )

    except Exception as exc:
        # 记录错误日志
        logger.error(
            f"邮箱验证邮件发送失败: user_id={user_id}, email={email}, "
            f"error={str(exc)}, retry_count={self.request.retries}",
            exc_info=True,
        )

        # 如果重试次数未达到上限，则重新抛出异常触发重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            # 达到最大重试次数，记录严重错误
            logger.critical(
                f"邮箱验证邮件发送最终失败（已重试{self.max_retries}次）: "
                f"user_id={user_id}, email={email}, error={str(exc)}"
            )
            raise  # 重新抛出异常，让Celery记录任务失败


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60秒后重试
    autoretry_for=(Exception,),  # 对所有异常自动重试
    retry_backoff=True,  # 指数退避
    retry_backoff_max=600,  # 最大退避时间600秒
    retry_jitter=True,  # 添加随机抖动避免同时重试
)
def send_password_reset_email(self, user_id, email, token):
    """
    发送密码重置邮件

    Args:
        user_id: 用户ID
        email: 用户邮箱
        token: 重置令牌

    Raises:
        Exception: 邮件发送失败时抛出异常，触发重试机制
    """
    try:
        # 构建重置链接（使用后端API URL）
        # 注意：这里使用后端API URL，前端会调用这个API
        backend_domain = getattr(settings, "BACKEND_DOMAIN", "http://localhost:8000")
        reset_url = f"{backend_domain}/api/auth/password/reset/?token={token}"

        # 邮件主题
        subject = "重置您的密码"

        # 渲染HTML模板
        html_content = render_to_string(
            "users/emails/password_reset.html",
            {"reset_url": reset_url},
        )

        # 渲染纯文本模板
        text_content = render_to_string(
            "users/emails/password_reset.txt",
            {"reset_url": reset_url},
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

        # 记录成功日志
        logger.info(
            f"密码重置邮件发送成功: user_id={user_id}, email={email}, "
            f"retry_count={self.request.retries}"
        )

    except Exception as exc:
        # 记录错误日志
        logger.error(
            f"密码重置邮件发送失败: user_id={user_id}, email={email}, "
            f"error={str(exc)}, retry_count={self.request.retries}",
            exc_info=True,
        )

        # 如果重试次数未达到上限，则重新抛出异常触发重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            # 达到最大重试次数，记录严重错误
            logger.critical(
                f"密码重置邮件发送最终失败（已重试{self.max_retries}次）: "
                f"user_id={user_id}, email={email}, error={str(exc)}"
            )
            raise  # 重新抛出异常，让Celery记录任务失败
