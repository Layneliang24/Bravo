# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_REGISTER-001, TC-AUTH_REGISTER-002, \
#   TC-AUTH_REGISTER-003, TC-AUTH_REGISTER-004, TC-AUTH_REGISTER-005, \
#   TC-AUTH_REGISTER-006, TC-AUTH_REGISTER-007, TC-AUTH_REGISTER-009, \
#   TC-AUTH_REGISTER-010
"""用户注册API集成测试

测试用户注册API的功能，包括成功注册、邮箱已存在、密码强度验证、验证码验证等场景。
预期这些测试在注册API未实现时会失败（Red阶段）。
"""

import json
import uuid

import pytest
from apps.users.utils import generate_captcha, store_captcha, verify_captcha
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings

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
class RegisterAPITests(TestCase):
    """用户注册API集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        cache.clear()

    def _get_valid_captcha(self):
        """获取有效的验证码"""
        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)
        return captcha_id, answer

    def test_register_api_endpoint_exists(self):
        """测试注册API端点存在"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        # 即使API未实现，也应该返回某种响应（不是404）
        self.assertNotEqual(response.status_code, 404)

    def test_register_success(self):
        """测试成功注册场景"""
        from unittest.mock import patch

        from apps.users.models import EmailVerification

        captcha_id, captcha_answer = self._get_valid_captcha()

        # Mock Celery任务
        with patch("apps.users.views.send_email_verification.delay") as mock_send_email:
            response = self.client.post(
                "/api/auth/register/",
                data=json.dumps(
                    {
                        "email": "newuser@example.com",
                        "password": "SecurePass123",
                        "password_confirm": "SecurePass123",
                        "captcha_id": captcha_id,
                        "captcha_answer": captcha_answer,
                    }
                ),
                content_type="application/json",
            )

            # 验证响应状态码
            self.assertEqual(response.status_code, 201)

            # 验证响应数据格式
            data = response.json()
            self.assertIn("user", data)
            self.assertIn("token", data)
            self.assertIn("refresh_token", data)
            self.assertIn("message", data)

            # 验证用户信息
            user_data = data["user"]
            self.assertEqual(user_data["email"], "newuser@example.com")
            self.assertFalse(user_data["is_email_verified"])

            # 验证用户已创建
            user = User.objects.get(email="newuser@example.com")
            self.assertIsNotNone(user)
            self.assertFalse(user.is_email_verified)

            # 验证Token存在
            self.assertIsNotNone(data["token"])
            self.assertIsNotNone(data["refresh_token"])

            # ✅ 验证EmailVerification记录已创建
            verification = EmailVerification.objects.filter(user=user).first()
            self.assertIsNotNone(verification, "注册时应该创建EmailVerification记录")
            self.assertEqual(verification.user, user)
            self.assertEqual(verification.email, user.email)
            self.assertIsNotNone(verification.token)
            self.assertIsNotNone(verification.expires_at)
            self.assertIsNone(verification.verified_at)

            # ✅ 验证邮件发送任务被调用
            self.assertTrue(mock_send_email.called, "注册时应该触发邮件发送任务")
            self.assertEqual(mock_send_email.call_count, 1)
            # 获取调用参数（call_args是((args,), {kwargs})格式）
            call_args_tuple = mock_send_email.call_args
            if call_args_tuple:
                # 位置参数在call_args[0]中
                args = call_args_tuple[0]
                if args and len(args) >= 3:
                    self.assertEqual(args[0], user.id)
                    self.assertEqual(args[1], user.email)
                    self.assertEqual(args[2], verification.token)
                else:
                    # 如果没有位置参数，检查关键字参数
                    kwargs = call_args_tuple[1] if len(call_args_tuple) > 1 else {}
                    if kwargs:
                        self.assertEqual(kwargs.get("user_id"), user.id)
                        self.assertEqual(kwargs.get("email"), user.email)
                        self.assertEqual(kwargs.get("token"), verification.token)

    def test_register_with_existing_email_fails(self):
        """测试使用已存在的邮箱注册失败"""
        # 先创建一个用户
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="OldPass123",
        )

        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "existing@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 应该返回400错误
        self.assertEqual(response.status_code, 400)

        # 验证错误信息
        data = response.json()
        self.assertIn("error", data)

    def test_register_with_weak_password_fails(self):
        """测试使用弱密码注册失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        # 测试密码太短
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "weakpass@example.com",
                    "password": "12345",  # 太短
                    "password_confirm": "12345",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

        # 测试密码只有数字
        captcha_id2, captcha_answer2 = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "weakpass2@example.com",
                    "password": "12345678",  # 只有数字
                    "password_confirm": "12345678",
                    "captcha_id": captcha_id2,
                    "captcha_answer": captcha_answer2,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

        # 测试密码只有字母
        captcha_id3, captcha_answer3 = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "weakpass3@example.com",
                    "password": "abcdefgh",  # 只有字母
                    "password_confirm": "abcdefgh",
                    "captcha_id": captcha_id3,
                    "captcha_answer": captcha_answer3,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_register_with_password_mismatch_fails(self):
        """测试密码和确认密码不匹配时注册失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "mismatch@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "DifferentPass123",  # 不匹配
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_register_with_invalid_captcha_fails(self):
        """测试验证码错误时注册失败"""
        captcha_id, _ = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "invalidcaptcha@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": "XXXX",  # 错误的验证码
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        # 验证错误代码
        self.assertIn("code", data)
        self.assertEqual(data["code"], "INVALID_CAPTCHA")

    def test_register_with_nonexistent_captcha_id_fails(self):
        """测试使用不存在的验证码ID时注册失败"""
        fake_captcha_id = str(uuid.uuid4())

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "nonexistentcaptcha@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": fake_captcha_id,
                    "captcha_answer": "ABCD",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["code"], "INVALID_CAPTCHA")

    def test_register_with_expired_captcha_fails(self):
        """测试使用过期的验证码时注册失败"""
        captcha_id, captcha_image, captcha_answer = generate_captcha()
        # 存储验证码但立即过期（expires_in=0）
        store_captcha(captcha_id, captcha_answer, expires_in=0)

        # 等待一下确保过期（在测试环境中可能不需要，但为了完整性）
        import time

        time.sleep(0.1)

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "expiredcaptcha@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["code"], "INVALID_CAPTCHA")

    def test_register_with_missing_fields_fails(self):
        """测试缺少必需字段时注册失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        # 缺少email
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 缺少password
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "missingpass@example.com",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 缺少captcha_id
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "missingcaptcha@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_register_creates_user_with_correct_fields(self):
        """测试注册时创建的用户包含正确的字段"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "correctfields@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        # 验证用户已创建
        user = User.objects.get(email="correctfields@example.com")
        self.assertIsNotNone(user)
        self.assertFalse(user.is_email_verified)
        self.assertEqual(user.email, "correctfields@example.com")
        # 验证密码已正确哈希
        self.assertTrue(user.check_password("SecurePass123"))

    def test_register_generates_jwt_tokens(self):
        """测试注册成功后生成JWT Token"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "jwttest@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()

        # 验证Token存在且格式正确（JWT Token通常是三段，用.分隔）
        self.assertIn("token", data)
        token = data["token"]
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
        # JWT Token格式：header.payload.signature
        token_parts = token.split(".")
        self.assertEqual(len(token_parts), 3)

        # 验证Refresh Token存在
        self.assertIn("refresh_token", data)
        refresh_token = data["refresh_token"]
        self.assertIsInstance(refresh_token, str)
        self.assertGreater(len(refresh_token), 0)
