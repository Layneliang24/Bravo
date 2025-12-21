# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_LOGIN-001, TC-AUTH_LOGIN-002, TC-AUTH_LOGIN-003, \
#   TC-AUTH_LOGIN-004, TC-AUTH_LOGIN-005, TC-AUTH_LOGIN-006, \
#   TC-AUTH_LOGIN-007, TC-AUTH_LOGIN-008, TC-AUTH_LOCK-001, \
#   TC-AUTH_LOCK-002, TC-AUTH_LOCK-003
"""用户登录API集成测试

测试用户登录API的功能，包括成功登录、密码错误、验证码错误、账户锁定、未激活邮箱等场景。
预期这些测试在登录API未实现时会失败（Red阶段）。
"""

import json
from datetime import datetime, timedelta

import pytest
from apps.users.utils import generate_captcha, store_captcha
from django.contrib.auth import get_user_model
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
class LoginAPITests(TestCase):
    """用户登录API集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        cache.clear()

        # 创建一个测试用户
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            is_email_verified=True,
        )

    def _get_valid_captcha(self):
        """获取有效的验证码"""
        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)
        return captcha_id, answer

    def test_login_api_endpoint_exists(self):
        """测试登录API端点存在"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        # 即使API未实现，也应该返回某种响应（不是404）
        self.assertNotEqual(response.status_code, 404)

    def test_login_success_with_email(self):
        """测试使用邮箱成功登录"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 验证响应状态码
        self.assertEqual(response.status_code, 200)

        # 验证响应数据格式
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("token", data)
        self.assertIn("refresh_token", data)

        # 验证用户信息
        user_data = data["user"]
        self.assertEqual(user_data["email"], "test@example.com")

        # 验证Token存在
        self.assertIsNotNone(data["token"])
        self.assertIsNotNone(data["refresh_token"])

        # 验证登录失败次数已重置
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.failed_login_attempts, 0)

    def test_login_success_with_username(self):
        """测试使用用户名成功登录"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "testuser",  # 使用用户名
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("refresh_token", data)

    def test_login_with_wrong_password_fails(self):
        """测试密码错误时登录失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "WrongPassword123",
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

        # 验证失败次数增加
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.failed_login_attempts, 1)

    def test_login_with_invalid_captcha_fails(self):
        """测试验证码错误时登录失败"""
        captcha_id, _ = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": "XXXX",  # 错误的验证码
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "INVALID_CAPTCHA")

    def test_login_with_nonexistent_user_fails(self):
        """测试使用不存在的用户登录失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "nonexistent@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_login_account_locked_after_5_failures(self):
        """测试5次登录失败后账户被锁定"""
        # 先失败4次
        for i in range(4):
            captcha_id, captcha_answer = self._get_valid_captcha()
            response = self.client.post(
                "/api/auth/login/",
                data=json.dumps(
                    {
                        "email": "test@example.com",
                        "password": "WrongPassword123",
                        "captcha_id": captcha_id,
                        "captcha_answer": captcha_answer,
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)

        # 第5次失败应该锁定账户
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "WrongPassword123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "ACCOUNT_LOCKED")

        # 验证账户被锁定
        self.test_user.refresh_from_db()
        self.assertIsNotNone(self.test_user.locked_until)
        self.assertGreater(self.test_user.locked_until, timezone.now())

    def test_login_locked_account_fails(self):
        """测试锁定期间尝试登录失败"""
        # 手动锁定账户
        self.test_user.locked_until = timezone.now() + timedelta(minutes=10)
        self.test_user.failed_login_attempts = 5
        self.test_user.save()

        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "ACCOUNT_LOCKED")

    def test_login_unlocks_after_lock_expires(self):
        """测试锁定过期后可以重新登录"""
        # 设置锁定时间为过去
        self.test_user.locked_until = timezone.now() - timedelta(minutes=1)
        self.test_user.failed_login_attempts = 5
        self.test_user.save()

        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 应该可以成功登录
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)

        # 验证失败次数已重置
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.failed_login_attempts, 0)
        self.assertIsNone(self.test_user.locked_until)

    def test_login_with_unverified_email_fails(self):
        """测试未验证邮箱的用户登录失败"""
        # 创建未验证邮箱的用户
        User.objects.create_user(
            username="unverified",
            email="unverified@example.com",
            password="SecurePass123",
            is_email_verified=False,
        )

        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "unverified@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "EMAIL_NOT_VERIFIED")

    def test_login_with_missing_fields_fails(self):
        """测试缺少必需字段时登录失败"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        # 缺少email
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 缺少password
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 缺少captcha_id
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_generates_jwt_tokens(self):
        """测试登录成功后生成JWT Token"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps(
                {
                    "email": "test@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 验证Token存在且格式正确（JWT Token通常是三段，用.分隔）
        self.assertIn("token", data)
        token = data["token"]
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
        token_parts = token.split(".")
        self.assertEqual(len(token_parts), 3)

        # 验证Refresh Token存在
        self.assertIn("refresh_token", data)
        refresh_token = data["refresh_token"]
        self.assertIsInstance(refresh_token, str)
        self.assertGreater(len(refresh_token), 0)
