# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_CAPTCHA-002
"""验证码API集成测试

测试获取验证码和刷新验证码API的功能和响应格式。
"""

import base64
import json
import uuid

import pytest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

# 测试时使用内存缓存模拟Redis
CACHES_TEST = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


@pytest.mark.integration
@override_settings(CACHES=CACHES_TEST)
class CaptchaAPITests(TestCase):
    """验证码API集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()

    def test_get_captcha_api_exists(self):
        """测试获取验证码API端点存在"""
        response = self.client.get("/api/auth/captcha/")
        self.assertEqual(response.status_code, 200)

    def test_get_captcha_api_response_format(self):
        """测试获取验证码API响应格式"""
        response = self.client.get("/api/auth/captcha/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # 验证响应包含必需字段
        self.assertIn("captcha_id", data)
        self.assertIn("captcha_image", data)
        self.assertIn("expires_in", data)

        # 验证字段类型和格式
        self.assertIsInstance(data["captcha_id"], str)
        self.assertIsInstance(data["captcha_image"], str)
        self.assertIsInstance(data["expires_in"], int)

        # 验证captcha_id是UUID格式
        try:
            uuid.UUID(data["captcha_id"])
        except ValueError:
            self.fail(f"captcha_id不是有效的UUID: {data['captcha_id']}")

        # 验证captcha_image是Base64编码的PNG格式
        self.assertTrue(data["captcha_image"].startswith("data:image/png;base64,"))
        base64_data = data["captcha_image"].replace("data:image/png;base64,", "")
        try:
            decoded = base64.b64decode(base64_data)
            self.assertGreater(len(decoded), 0)
        except Exception as e:
            self.fail(f"Base64解码失败: {e}")

        # 验证expires_in为300秒
        self.assertEqual(data["expires_in"], 300)

    def test_get_captcha_api_generates_different_captchas(self):
        """测试每次获取验证码都生成不同的验证码"""
        response1 = self.client.get("/api/auth/captcha/")
        response2 = self.client.get("/api/auth/captcha/")

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        data1 = response1.json()
        data2 = response2.json()

        # 验证码ID应该不同
        self.assertNotEqual(data1["captcha_id"], data2["captcha_id"])
        # 验证码图片应该不同（Base64编码不同）
        self.assertNotEqual(data1["captcha_image"], data2["captcha_image"])

    def test_refresh_captcha_api_exists(self):
        """测试刷新验证码API端点存在"""
        response = self.client.post(
            "/api/auth/captcha/refresh/",
            data=json.dumps({"captcha_id": str(uuid.uuid4())}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_refresh_captcha_api_response_format(self):
        """测试刷新验证码API响应格式"""
        response = self.client.post(
            "/api/auth/captcha/refresh/",
            data=json.dumps({"captcha_id": str(uuid.uuid4())}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # 验证响应包含必需字段
        self.assertIn("captcha_id", data)
        self.assertIn("captcha_image", data)
        self.assertIn("expires_in", data)

        # 验证字段类型和格式
        self.assertIsInstance(data["captcha_id"], str)
        self.assertIsInstance(data["captcha_image"], str)
        self.assertIsInstance(data["expires_in"], int)

        # 验证captcha_id是UUID格式
        try:
            uuid.UUID(data["captcha_id"])
        except ValueError:
            self.fail(f"captcha_id不是有效的UUID: {data['captcha_id']}")

        # 验证captcha_image是Base64编码的PNG格式
        self.assertTrue(data["captcha_image"].startswith("data:image/png;base64,"))
        base64_data = data["captcha_image"].replace("data:image/png;base64,", "")
        try:
            decoded = base64.b64decode(base64_data)
            self.assertGreater(len(decoded), 0)
        except Exception as e:
            self.fail(f"Base64解码失败: {e}")

        # 验证expires_in为300秒
        self.assertEqual(data["expires_in"], 300)

    def test_refresh_captcha_api_generates_new_captcha(self):
        """测试刷新验证码API生成新的验证码"""
        # 先获取一个验证码
        response1 = self.client.get("/api/auth/captcha/")
        data1 = response1.json()
        old_captcha_id = data1["captcha_id"]

        # 刷新验证码
        response2 = self.client.post(
            "/api/auth/captcha/refresh/",
            data=json.dumps({"captcha_id": old_captcha_id}),
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 200)

        data2 = response2.json()
        # 新的验证码ID应该不同
        self.assertNotEqual(old_captcha_id, data2["captcha_id"])
        # 新的验证码图片应该不同
        self.assertNotEqual(data1["captcha_image"], data2["captcha_image"])
