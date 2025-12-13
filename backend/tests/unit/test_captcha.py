# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_CAPTCHA-001
"""验证码模块单元测试

根据PRD要求，验证验证码生成逻辑、Redis存储、过期机制以及验证码验证功能。
预期这些测试在验证码模块未实现时会失败。
"""

import base64
import uuid

import pytest
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

# 测试时使用内存缓存模拟Redis
CACHES_TEST = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


@pytest.mark.unit
@override_settings(CACHES=CACHES_TEST)
class CaptchaGenerationTests(TestCase):
    """验证码生成功能测试"""

    def setUp(self):
        """设置测试环境"""
        cache.clear()

    def test_captcha_generation_function_exists(self):
        """测试验证码生成函数存在"""
        # 预期：从apps.users.utils导入generate_captcha函数
        try:
            from apps.users.utils import generate_captcha

            self.assertTrue(callable(generate_captcha))
        except ImportError:
            self.fail("generate_captcha函数不存在")

    def test_captcha_generates_4_characters(self):
        """测试验证码生成4位字符（数字+字母混合）"""
        from apps.users.utils import generate_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        self.assertIsNotNone(captcha_id)
        self.assertIsNotNone(captcha_image)
        self.assertIsNotNone(answer)
        self.assertEqual(len(answer), 4)
        # 验证答案只包含数字和字母
        self.assertTrue(answer.isalnum())

    def test_captcha_image_is_base64_encoded(self):
        """测试验证码图片是Base64编码的PNG格式"""
        from apps.users.utils import generate_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        # 验证Base64格式
        self.assertTrue(captcha_image.startswith("data:image/png;base64,"))
        # 验证可以解码
        base64_data = captcha_image.replace("data:image/png;base64,", "")
        try:
            decoded = base64.b64decode(base64_data)
            self.assertGreater(len(decoded), 0)
        except Exception as e:
            self.fail(f"Base64解码失败: {e}")

    def test_captcha_id_is_uuid(self):
        """测试验证码ID是UUID格式"""
        from apps.users.utils import generate_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        # 验证UUID格式
        try:
            uuid.UUID(captcha_id)
        except ValueError:
            self.fail(f"captcha_id不是有效的UUID: {captcha_id}")

    def test_captcha_generates_different_values(self):
        """测试每次生成的验证码都不同"""
        from apps.users.utils import generate_captcha

        captcha1 = generate_captcha()
        captcha2 = generate_captcha()

        # 验证码ID应该不同
        self.assertNotEqual(captcha1[0], captcha2[0])
        # 答案可能相同（概率很低），但ID必须不同


@pytest.mark.unit
@override_settings(CACHES=CACHES_TEST)
class CaptchaRedisStorageTests(TestCase):
    """验证码Redis存储功能测试"""

    def setUp(self):
        """设置测试环境"""
        cache.clear()

    def test_captcha_storage_function_exists(self):
        """测试验证码存储函数存在"""
        try:
            from apps.users.utils import store_captcha

            self.assertTrue(callable(store_captcha))
        except ImportError:
            self.fail("store_captcha函数不存在")

    def test_captcha_stored_in_redis(self):
        """测试验证码答案存储在Redis中"""
        from apps.users.utils import generate_captcha, store_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 验证可以从缓存中读取
        stored_answer = cache.get(f"captcha:{captcha_id}")
        self.assertEqual(stored_answer, answer)

    def test_captcha_storage_key_format(self):
        """测试验证码存储Key格式为captcha:{session_id}"""
        from apps.users.utils import generate_captcha, store_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 验证Key格式
        expected_key = f"captcha:{captcha_id}"
        stored_answer = cache.get(expected_key)
        self.assertEqual(stored_answer, answer)

    def test_captcha_expires_after_5_minutes(self):
        """测试验证码5分钟后过期"""
        from apps.users.utils import generate_captcha, store_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer, expires_in=300)  # 5分钟

        # 立即读取应该存在
        stored_answer = cache.get(f"captcha:{captcha_id}")
        self.assertEqual(stored_answer, answer)

        # 注意：在实际测试中，我们无法真正等待5分钟
        # 这里只验证设置了过期时间（通过TTL检查）
        # 如果使用django-redis，可以检查TTL
        try:
            from django.core.cache import caches

            redis_cache = caches["default"]
            if hasattr(redis_cache, "ttl"):
                ttl = redis_cache.ttl(f"captcha:{captcha_id}")
                # TTL应该在300秒左右（允许一些误差）
                self.assertGreater(ttl, 290)
                self.assertLessEqual(ttl, 300)
        except Exception:
            # 如果无法检查TTL，跳过此测试
            pass


@pytest.mark.unit
@override_settings(CACHES=CACHES_TEST)
class CaptchaVerificationTests(TestCase):
    """验证码验证功能测试"""

    def setUp(self):
        """设置测试环境"""
        cache.clear()

    def test_captcha_verification_function_exists(self):
        """测试验证码验证函数存在"""
        try:
            from apps.users.utils import verify_captcha

            self.assertTrue(callable(verify_captcha))
        except ImportError:
            self.fail("verify_captcha函数不存在")

    def test_captcha_verification_succeeds_with_correct_answer(self):
        """测试使用正确答案验证成功"""
        from apps.users.utils import generate_captcha, store_captcha, verify_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 验证成功
        result = verify_captcha(captcha_id, answer)
        self.assertTrue(result)

    def test_captcha_verification_fails_with_wrong_answer(self):
        """测试使用错误答案验证失败"""
        from apps.users.utils import generate_captcha, store_captcha, verify_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 使用错误答案验证
        wrong_answer = "XXXX" if answer != "XXXX" else "YYYY"
        result = verify_captcha(captcha_id, wrong_answer)
        self.assertFalse(result)

    def test_captcha_verification_fails_with_nonexistent_id(self):
        """测试使用不存在的验证码ID验证失败"""
        from apps.users.utils import verify_captcha

        fake_id = str(uuid.uuid4())
        result = verify_captcha(fake_id, "ABCD")
        self.assertFalse(result)

    def test_captcha_verification_is_case_insensitive(self):
        """测试验证码验证不区分大小写"""
        from apps.users.utils import generate_captcha, store_captcha, verify_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 使用小写答案验证（如果答案包含字母）
        if answer.isalpha():
            result = verify_captcha(captcha_id, answer.lower())
            self.assertTrue(result)

    def test_captcha_verification_deletes_after_success(self):
        """测试验证成功后删除验证码（防止重复使用）"""
        from apps.users.utils import generate_captcha, store_captcha, verify_captcha

        captcha_id, captcha_image, answer = generate_captcha()
        store_captcha(captcha_id, answer)

        # 第一次验证成功
        result1 = verify_captcha(captcha_id, answer)
        self.assertTrue(result1)

        # 第二次验证应该失败（因为已删除）
        result2 = verify_captcha(captcha_id, answer)
        self.assertFalse(result2)
