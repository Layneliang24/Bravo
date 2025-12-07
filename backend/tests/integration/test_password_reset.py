# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""密码找回API集成测试

测试密码找回API的功能，包括发送重置邮件、重置密码等场景。
预期这些测试在密码找回API未实现时会失败（Red阶段）。
"""

import json
from datetime import timedelta

import pytest
from apps.users.models import PasswordReset
from apps.users.utils import generate_captcha, store_captcha
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.utils import timezone

User = get_user_model()

# 测试时使用内存缓存模拟Redis
CACHES_TEST = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


@pytest.mark.integration
@pytest.mark.django_db
@override_settings(CACHES=CACHES_TEST)
class PasswordResetAPITests(TestCase):
    """密码找回API集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        mail.outbox.clear()
        cache.clear()

        # 创建测试用户
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            is_email_verified=True,  # 密码找回需要已验证的邮箱
        )

    def _get_valid_captcha(self):
        """获取有效的验证码"""
        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)
        return captcha_id, answer

    # ========== 发送密码重置邮件API测试 ==========

    def test_send_password_reset_email_api_endpoint_exists(self):
        """测试发送密码重置邮件API端点存在"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        # 预期端点存在（即使返回错误，也应该是400/404，而不是500）
        self.assertNotEqual(response.status_code, 500)
        # 使用response避免flake8警告
        _ = response

    def test_send_password_reset_email_requires_captcha(self):
        """测试发送密码重置邮件需要验证码"""
        response = self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
        )
        # 预期返回400（缺少验证码）
        self.assertEqual(response.status_code, 400)

    def test_send_password_reset_email_creates_reset_record(self):
        """测试发送密码重置邮件会创建PasswordReset记录"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 预期创建了PasswordReset记录
        reset = PasswordReset.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(reset)
        self.assertEqual(reset.user, self.test_user)
        self.assertIsNotNone(reset.token)
        self.assertIsNotNone(reset.expires_at)
        self.assertIsNone(reset.used_at)

    def test_send_password_reset_email_triggers_celery_task(self):
        """测试发送密码重置邮件会触发Celery任务发送邮件"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 预期邮件被发送（测试环境CELERY_TASK_ALWAYS_EAGER=True，会同步执行）
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["test@example.com"])
        self.assertIn("重置", email.subject)

    def test_send_password_reset_email_contains_reset_link(self):
        """测试重置邮件包含重置链接"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 预期邮件包含重置链接
        reset = PasswordReset.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(reset)
        email = mail.outbox[0]
        self.assertIn(reset.token, email.body)

    def test_send_password_reset_email_returns_success_message(self):
        """测试发送密码重置邮件返回成功消息"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 预期返回200和成功消息
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("message", data)
        self.assertIn("重置", data["message"])

    def test_send_password_reset_email_with_nonexistent_email(self):
        """测试使用不存在的邮箱发送重置邮件（防止用户枚举）"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "nonexistent@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 预期仍然返回200（防止用户枚举攻击）
        self.assertEqual(response.status_code, 200)
        # 预期没有创建PasswordReset记录
        reset = PasswordReset.objects.filter(
            user__email="nonexistent@example.com"
        ).first()
        self.assertIsNone(reset)

    def test_send_password_reset_email_with_invalid_captcha_fails(self):
        """测试使用无效验证码发送重置邮件失败"""
        response = self.client.post(
            "/api/auth/password/reset/send/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": "invalid-id",
                    "captcha_answer": "wrong-answer",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data or {})

    # ========== 重置密码API测试 ==========

    def test_reset_password_api_endpoint_exists(self):
        """测试重置密码API端点存在"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )
        # 预期端点存在（即使返回错误，也应该是400/404，而不是500）
        self.assertNotEqual(response.status_code, 500)
        # 使用response避免flake8警告
        _ = response

    def test_reset_password_with_valid_token_succeeds(self):
        """测试使用有效token重置密码成功"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )

        # 预期返回200和成功消息
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("message", data)
        self.assertIn("成功", data["message"])

    def test_reset_password_updates_user_password(self):
        """测试重置密码会更新用户密码"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        new_password = "NewSecurePass123"

        self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": new_password,
                    "password_confirm": new_password,
                }
            ),
            content_type="application/json",
        )

        # 验证密码已更新
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password(new_password))

    def test_reset_password_marks_reset_as_used(self):
        """测试重置密码会标记PasswordReset为已使用"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )

        # 预期PasswordReset被标记为已使用
        reset.refresh_from_db()
        self.assertIsNotNone(reset.used_at)

    def test_reset_password_with_invalid_token_fails(self):
        """测试使用无效token重置密码失败"""
        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": "invalid-token-123",
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400或404
        self.assertIn(response.status_code, [400, 404])
        data = json.loads(response.content)
        self.assertIn("error", data or {})

    def test_reset_password_with_expired_token_fails(self):
        """测试使用过期token重置密码失败"""
        # 创建已过期的重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="expired-token-123",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("过期", data["error"])

    def test_reset_password_with_already_used_token_fails(self):
        """测试使用已使用的token重置密码失败"""
        # 创建已使用的重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="used-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
            used_at=timezone.now(),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "NewSecurePass123",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("已使用", data["error"])

    def test_reset_password_with_password_mismatch_fails(self):
        """测试密码和确认密码不匹配时重置失败"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "NewSecurePass123",
                    "password_confirm": "DifferentPass123",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data or {})

    def test_reset_password_with_weak_password_fails(self):
        """测试使用弱密码重置失败"""
        # 创建重置记录
        reset = PasswordReset.objects.create(
            user=self.test_user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        response = self.client.post(
            "/api/auth/password/reset/",
            data=json.dumps(
                {
                    "token": reset.token,
                    "password": "123456",  # 太短且只有数字
                    "password_confirm": "123456",
                }
            ),
            content_type="application/json",
        )

        # 预期返回400
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data or {})
