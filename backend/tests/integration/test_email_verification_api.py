# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_EMAIL-001, TC-AUTH_EMAIL-002, TC-AUTH_EMAIL-003, \
#   TC-AUTH_EMAIL-004, TC-AUTH_EMAIL-005, TC-AUTH_EMAIL-006
"""邮箱验证API集成测试

测试邮箱验证API的功能，包括发送验证邮件、验证邮箱链接等场景。
预期这些测试在邮箱验证API未实现时会失败（Red阶段）。
"""

import json
from datetime import timedelta

import pytest
from apps.users.models import EmailVerification
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class EmailVerificationAPITests(TestCase):
    """邮箱验证API集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        mail.outbox.clear()

        # 创建测试用户
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            is_email_verified=False,
        )

    def _get_auth_headers(self):
        """获取JWT认证头"""
        refresh = RefreshToken.for_user(self.test_user)
        access_token = str(refresh.access_token)
        return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    def test_send_verification_email_api_endpoint_exists(self):
        """测试发送验证邮件API端点存在"""
        headers = self._get_auth_headers()
        response = self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
            **headers,
        )
        # 预期端点存在（即使返回错误，也应该是400/401/403，而不是404）
        self.assertNotEqual(response.status_code, 404)
        # 使用response避免flake8警告
        _ = response

    def test_send_verification_email_requires_authentication(self):
        """测试发送验证邮件需要认证"""
        response = self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
        )
        # 预期返回401未授权
        self.assertEqual(response.status_code, 401)

    def test_send_verification_email_creates_verification_record(self):
        """测试发送验证邮件会创建EmailVerification记录"""
        headers = self._get_auth_headers()
        self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
            **headers,
        )

        # 预期创建了EmailVerification记录
        verification = EmailVerification.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(verification)
        self.assertEqual(verification.user, self.test_user)
        self.assertEqual(verification.email, "test@example.com")
        self.assertIsNotNone(verification.token)
        self.assertIsNotNone(verification.expires_at)
        self.assertIsNone(verification.verified_at)

    def test_send_verification_email_triggers_celery_task(self):
        """测试发送验证邮件会触发Celery任务发送邮件"""
        headers = self._get_auth_headers()
        self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
            **headers,
        )

        # 预期邮件被发送（测试环境CELERY_TASK_ALWAYS_EAGER=True，会同步执行）
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["test@example.com"])
        self.assertIn("验证", email.subject)

    def test_send_verification_email_contains_verification_link(self):
        """测试验证邮件包含验证链接"""
        headers = self._get_auth_headers()
        self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
            **headers,
        )

        # 预期邮件包含验证链接
        verification = EmailVerification.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(verification)
        email = mail.outbox[0]
        self.assertIn(verification.token, email.body)

    def test_send_verification_email_returns_success_message(self):
        """测试发送验证邮件返回成功消息"""
        headers = self._get_auth_headers()
        response = self.client.post(
            "/api/auth/email/verify/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
            **headers,
        )

        # 预期返回200和成功消息
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("message", data)
        self.assertIn("验证邮件", data["message"])

    def test_verify_email_api_endpoint_exists(self):
        """测试验证邮箱API端点存在"""
        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.get(f"/api/auth/email/verify/{verification.token}/")
        # 预期端点存在（即使返回错误，也应该是400/404，而不是500）
        self.assertNotEqual(response.status_code, 500)
        # 使用response避免flake8警告
        _ = response

    def test_verify_email_with_valid_token_succeeds(self):
        """测试使用有效token验证邮箱成功"""
        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.get(f"/api/auth/email/verify/{verification.token}/")

        # 预期返回200和成功消息
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("message", data)
        self.assertIn("验证成功", data["message"])

    def test_verify_email_updates_user_status(self):
        """测试验证邮箱会更新用户状态"""
        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        # 验证前用户状态
        self.assertFalse(self.test_user.is_email_verified)
        self.assertIsNone(self.test_user.email_verified_at)

        self.client.get(f"/api/auth/email/verify/{verification.token}/")

        # 验证后用户状态
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_email_verified)
        self.assertIsNotNone(self.test_user.email_verified_at)

    def test_verify_email_marks_verification_as_verified(self):
        """测试验证邮箱会标记EmailVerification为已验证"""
        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        self.client.get(f"/api/auth/email/verify/{verification.token}/")

        # 预期EmailVerification被标记为已验证
        verification.refresh_from_db()
        self.assertIsNotNone(verification.verified_at)

    def test_verify_email_with_invalid_token_fails(self):
        """测试使用无效token验证邮箱失败"""
        response = self.client.get("/api/auth/email/verify/invalid-token-123/")

        # 预期返回400或404
        self.assertIn(response.status_code, [400, 404])
        data = json.loads(response.content)
        self.assertIn("error", data or {})

    def test_verify_email_with_expired_token_fails(self):
        """测试使用过期token验证邮箱失败"""
        # 创建已过期的验证记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="expired-token-123",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get(f"/api/auth/email/verify/{verification.token}/")

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("过期", data["error"])

    def test_verify_email_with_already_verified_token_fails(self):
        """测试使用已验证的token再次验证失败"""
        # 创建已验证的记录
        verification = EmailVerification.objects.create(
            user=self.test_user,
            email="test@example.com",
            token="verified-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
            verified_at=timezone.now(),
        )

        response = self.client.get(f"/api/auth/email/verify/{verification.token}/")

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("已验证", data["error"])
