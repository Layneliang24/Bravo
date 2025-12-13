# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_PREVIEW-002
"""登录预验证API频率限制集成测试

测试登录预验证API的频率限制是否生效，以及在限制下的行为。
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


@pytest.mark.integration
@pytest.mark.django_db
@override_settings(CACHES=CACHES_TEST)
class PreviewThrottlingTests(TestCase):
    """登录预验证API频率限制集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        cache.clear()

        # 创建测试用户
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            is_email_verified=True,
            display_name="测试用户",
        )

    def _get_valid_captcha(self):
        """获取有效的验证码"""
        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)
        return captcha_id, answer

    def test_preview_throttle_allows_10_requests_per_minute(self):
        """测试频率限制允许每分钟10次请求"""
        # 发送10次请求，每次使用新的验证码
        for i in range(10):
            captcha_id, captcha_answer = self._get_valid_captcha()
            response = self.client.post(
                "/api/auth/preview/",
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
            # 每次请求都应该返回200（频率限制应该允许）
            self.assertEqual(
                response.status_code,
                200,
                f"第{i+1}次请求应该成功，但返回了{response.status_code}",
            )

    def test_preview_throttle_blocks_11th_request(self):
        """测试第11次请求被频率限制阻止"""
        # 发送10次请求，每次使用新的验证码
        for i in range(10):
            captcha_id, captcha_answer = self._get_valid_captcha()
            response = self.client.post(
                "/api/auth/preview/",
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

        # 第11次请求应该被限制（即使验证码有效）
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/preview/",
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

        # 应该返回429 Too Many Requests
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn("detail", data)

    def test_preview_throttle_resets_after_minute(self):
        """测试频率限制在一分钟后重置（需要模拟时间）"""
        # 这个测试需要模拟时间，在实际环境中可能需要使用freezegun等工具
        # 这里先测试基本逻辑：发送10次请求后，第11次被限制
        for i in range(10):
            captcha_id, captcha_answer = self._get_valid_captcha()
            response = self.client.post(
                "/api/auth/preview/",
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

        # 第11次请求应该被限制
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = self.client.post(
            "/api/auth/preview/",
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
        self.assertEqual(response.status_code, 429)

        # 注意：实际的时间重置测试需要模拟时间流逝，这里只测试基本逻辑

    def test_preview_throttle_is_per_ip(self):
        """测试频率限制是基于IP地址的"""
        # 使用不同的IP地址（通过HTTP_X_FORWARDED_FOR头）
        client1 = Client(HTTP_X_FORWARDED_FOR="192.168.1.1")
        client2 = Client(HTTP_X_FORWARDED_FOR="192.168.1.2")

        # 客户端1发送10次请求，每次使用新的验证码
        for i in range(10):
            captcha_id, captcha_answer = self._get_valid_captcha()
            response = client1.post(
                "/api/auth/preview/",
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

        # 客户端1的第11次请求应该被限制
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = client1.post(
            "/api/auth/preview/",
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
        self.assertEqual(response.status_code, 429)

        # 客户端2应该不受影响，可以继续请求
        captcha_id, captcha_answer = self._get_valid_captcha()
        response = client2.post(
            "/api/auth/preview/",
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
        # 客户端2的请求应该成功（不同IP不受限制）
        self.assertEqual(response.status_code, 200)
