# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""登录预验证API单元测试

测试登录预验证API的功能，包括正确账号密码返回头像信息、错误账号密码返回valid: false、
无头像用户返回默认头像信息等场景。
预期这些测试在预验证API未实现时会失败（Red阶段）。
"""

import json

import pytest
from apps.users.utils import generate_captcha, store_captcha
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


@pytest.mark.unit
@pytest.mark.django_db
@override_settings(CACHES=CACHES_TEST)
class PreviewAPITests(TestCase):
    """登录预验证API单元测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        cache.clear()

        # 创建测试用户（有头像）
        self.user_with_avatar = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="SecurePass123",
            is_email_verified=True,
            display_name="测试用户1",
            avatar="https://example.com/avatars/user1.jpg",
        )

        # 创建测试用户（无头像）
        self.user_without_avatar = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="SecurePass123",
            is_email_verified=True,
            display_name="测试用户2",
            avatar=None,
        )

        # 创建测试用户（无头像，无display_name，使用username）
        self.user_no_display_name = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="SecurePass123",
            is_email_verified=True,
            display_name=None,
            avatar=None,
        )

    def _get_valid_captcha(self):
        """获取有效的验证码"""
        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)
        return captcha_id, answer

    def test_preview_api_endpoint_exists(self):
        """测试预验证API端点存在"""
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        # 即使API未实现，也应该返回某种响应（不是404）
        self.assertNotEqual(response.status_code, 404)

    def test_preview_with_correct_credentials_returns_avatar(self):
        """测试正确账号密码返回头像信息"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 应该返回200状态码
        self.assertEqual(response.status_code, 200)

        # 验证响应数据格式
        data = response.json()
        self.assertTrue(data["valid"])
        self.assertIn("user", data)
        self.assertIsNotNone(data["user"])

        # 验证用户信息
        user_data = data["user"]
        self.assertEqual(user_data["display_name"], "测试用户1")
        self.assertEqual(
            user_data["avatar_url"], "https://example.com/avatars/user1.jpg"
        )
        self.assertFalse(user_data["default_avatar"])

    def test_preview_with_correct_credentials_no_avatar_returns_default(self):
        """测试正确账号密码但无头像时返回默认头像信息"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test2@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        self.assertIn("user", data)

        # 验证默认头像信息
        user_data = data["user"]
        self.assertEqual(user_data["display_name"], "测试用户2")
        self.assertIsNone(user_data["avatar_url"])
        self.assertTrue(user_data["default_avatar"])
        self.assertIn("avatar_letter", user_data)
        # 应该返回display_name的首字母
        self.assertEqual(user_data["avatar_letter"], "测")

    def test_preview_with_no_display_name_uses_username(self):
        """测试无display_name时使用username生成avatar_letter"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test3@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])

        user_data = data["user"]
        # display_name应该为None或username
        self.assertIn("avatar_letter", user_data)
        # 应该返回username的首字母（大写）
        self.assertEqual(user_data["avatar_letter"], "T")

    def test_preview_with_wrong_password_returns_invalid(self):
        """测试错误密码返回valid: false"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "WrongPassword123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        # 应该返回200状态码（安全考虑）
        self.assertEqual(response.status_code, 200)

        # 验证响应数据
        data = response.json()
        self.assertFalse(data["valid"])
        self.assertIsNone(data.get("user"))

    def test_preview_with_nonexistent_user_returns_invalid(self):
        """测试不存在的用户返回valid: false"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
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

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["valid"])
        self.assertIsNone(data.get("user"))

    def test_preview_with_invalid_captcha_returns_error(self):
        """测试验证码错误时返回错误"""
        captcha_id, _ = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": "XXXX",  # 错误的验证码
                }
            ),
            content_type="application/json",
        )

        # 验证码错误应该返回400
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "INVALID_CAPTCHA")

    def test_preview_with_missing_fields_returns_error(self):
        """测试缺少必需字段时返回错误"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        # 缺少email
        response = self.client.post(
            "/api/auth/preview/",
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
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 缺少captcha_id
        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "SecurePass123",
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_preview_supports_username_login(self):
        """测试支持使用用户名登录"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "testuser1",  # 使用用户名
                    "password": "SecurePass123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        self.assertIn("user", data)

    def test_preview_does_not_increment_failed_login_attempts(self):
        """测试预验证不会增加登录失败次数"""
        captcha_id, captcha_answer = self._get_valid_captcha()

        # 记录初始失败次数
        initial_attempts = self.user_with_avatar.failed_login_attempts

        # 使用错误密码进行预验证
        response = self.client.post(
            "/api/auth/preview/",
            data=json.dumps(
                {
                    "email": "test1@example.com",
                    "password": "WrongPassword123",
                    "captcha_id": captcha_id,
                    "captcha_answer": captcha_answer,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # 验证失败次数没有增加
        self.user_with_avatar.refresh_from_db()
        self.assertEqual(self.user_with_avatar.failed_login_attempts, initial_attempts)
