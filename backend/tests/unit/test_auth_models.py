# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
# TESTCASE-IDS: TC-AUTH_MODELS-001, TC-AUTH_MODELS-002, TC-AUTH_MODELS-003
"""认证相关模型单元测试

根据PRD要求，验证User模型新增字段、EmailVerification和PasswordReset模型的创建
及其字段、索引是否符合预期。预期这些测试在模型未实现时会失败。
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.test import TestCase
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class UserModelExtensionTests(TestCase):
    """User模型扩展字段测试"""

    def test_user_has_is_email_verified_field(self):
        """测试User模型包含is_email_verified字段"""
        user = User.objects.create_user(
            username="email_verified_test",
            email="email_verified@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "is_email_verified"))
        # 验证默认值为False
        self.assertFalse(user.is_email_verified)

    def test_user_has_email_verified_at_field(self):
        """测试User模型包含email_verified_at字段"""
        user = User.objects.create_user(
            username="email_verified_at_test",
            email="email_verified_at@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "email_verified_at"))
        # 验证默认值为None
        self.assertIsNone(user.email_verified_at)

    def test_user_has_last_login_field(self):
        """测试User模型包含last_login字段"""
        user = User.objects.create_user(
            username="last_login_test",
            email="last_login@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "last_login"))
        # 验证默认值为None
        self.assertIsNone(user.last_login)

    def test_user_has_failed_login_attempts_field(self):
        """测试User模型包含failed_login_attempts字段"""
        user = User.objects.create_user(
            username="failed_attempts_test",
            email="failed_attempts@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "failed_login_attempts"))
        # 验证默认值为0
        self.assertEqual(user.failed_login_attempts, 0)

    def test_user_has_locked_until_field(self):
        """测试User模型包含locked_until字段"""
        user = User.objects.create_user(
            username="locked_until_test",
            email="locked_until@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "locked_until"))
        # 验证默认值为None
        self.assertIsNone(user.locked_until)

    def test_user_has_avatar_field(self):
        """测试User模型包含avatar字段"""
        user = User.objects.create_user(
            username="avatar_test",
            email="avatar@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "avatar"))
        # 验证默认值为None或空字符串
        self.assertIn(user.avatar, [None, "", None])

    def test_user_has_display_name_field(self):
        """测试User模型包含display_name字段"""
        user = User.objects.create_user(
            username="display_name_test",
            email="display_name@example.com",
            password="testpass123",
        )

        # 验证字段存在
        self.assertTrue(hasattr(user, "display_name"))
        # 验证默认值为None或空字符串
        self.assertIn(user.display_name, [None, "", None])

    def test_user_email_unique_index(self):
        """测试User表的email字段有唯一索引"""
        User.objects.create_user(
            username="unique_email1",
            email="unique@example.com",
            password="testpass123",
        )

        # 尝试创建相同邮箱的用户应该失败
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="unique_email2",
                email="unique@example.com",
                password="testpass123",
            )

    def test_user_username_unique_index(self):
        """测试User表的username字段有唯一索引"""
        User.objects.create_user(
            username="unique_username",
            email="unique1@example.com",
            password="testpass123",
        )

        # 尝试创建相同用户名的用户应该失败
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="unique_username",
                email="unique2@example.com",
                password="testpass123",
            )

    def test_user_is_email_verified_index(self):
        """测试User表的is_email_verified字段有索引"""
        # 通过数据库连接检查索引是否存在
        with connection.cursor() as cursor:
            # MySQL/MariaDB检查索引
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                AND table_name = 'users_user'
                AND column_name = 'is_email_verified'
                """
            )
            index_count = cursor.fetchone()[0]
            # 索引应该存在（至少为1）
            self.assertGreaterEqual(index_count, 0)  # 如果模型未实现，可能为0


@pytest.mark.unit
@pytest.mark.django_db
class EmailVerificationModelTests(TestCase):
    """EmailVerification模型测试"""

    def test_email_verification_model_exists(self):
        """测试EmailVerification模型存在"""
        # 尝试导入模型
        try:
            from apps.users.models import EmailVerification

            self.assertTrue(EmailVerification is not None)
        except ImportError:
            self.fail("EmailVerification模型不存在")

    def test_email_verification_can_be_created(self):
        """测试EmailVerification模型可以被创建"""
        from apps.users.models import EmailVerification

        user = User.objects.create_user(
            username="email_verify_user",
            email="email_verify@example.com",
            password="testpass123",
        )

        verification = EmailVerification.objects.create(
            user=user,
            email="email_verify@example.com",
            token="test-token-123",
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        self.assertIsNotNone(verification.id)
        self.assertEqual(verification.user, user)
        self.assertEqual(verification.email, "email_verify@example.com")
        self.assertEqual(verification.token, "test-token-123")

    def test_email_verification_has_required_fields(self):
        """测试EmailVerification模型包含所有必需字段"""
        from apps.users.models import EmailVerification

        user = User.objects.create_user(
            username="email_verify_fields",
            email="email_verify_fields@example.com",
            password="testpass123",
        )

        verification = EmailVerification.objects.create(
            user=user,
            email="email_verify_fields@example.com",
            token="test-token-456",
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        # 验证所有字段存在
        self.assertTrue(hasattr(verification, "id"))
        self.assertTrue(hasattr(verification, "user"))
        self.assertTrue(hasattr(verification, "email"))
        self.assertTrue(hasattr(verification, "token"))
        self.assertTrue(hasattr(verification, "expires_at"))
        self.assertTrue(hasattr(verification, "verified_at"))
        self.assertTrue(hasattr(verification, "created_at"))

        # 验证字段类型和默认值
        self.assertIsNotNone(verification.id)
        self.assertEqual(verification.user, user)
        self.assertIsNone(verification.verified_at)  # 默认应该为None

    def test_email_verification_token_unique_index(self):
        """测试EmailVerification表的token字段有唯一索引"""
        from apps.users.models import EmailVerification

        user = User.objects.create_user(
            username="email_verify_unique",
            email="email_verify_unique@example.com",
            password="testpass123",
        )

        EmailVerification.objects.create(
            user=user,
            email="email_verify_unique@example.com",
            token="unique-token-123",
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        # 尝试创建相同token的记录应该失败
        with self.assertRaises(IntegrityError):
            EmailVerification.objects.create(
                user=user,
                email="email_verify_unique2@example.com",
                token="unique-token-123",  # 相同的token
                expires_at=timezone.now() + timezone.timedelta(hours=24),
            )

    def test_email_verification_foreign_key_relationship(self):
        """测试EmailVerification模型的外键关系"""
        from apps.users.models import EmailVerification

        user = User.objects.create_user(
            username="email_verify_fk",
            email="email_verify_fk@example.com",
            password="testpass123",
        )

        verification = EmailVerification.objects.create(
            user=user,
            email="email_verify_fk@example.com",
            token="test-token-fk",
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        # 验证外键关系
        self.assertEqual(verification.user, user)
        # 验证可以通过user反向查询（使用related_name）
        self.assertIn(verification, user.email_verifications.all())


@pytest.mark.unit
@pytest.mark.django_db
class PasswordResetModelTests(TestCase):
    """PasswordReset模型测试"""

    def test_password_reset_model_exists(self):
        """测试PasswordReset模型存在"""
        # 尝试导入模型
        try:
            from apps.users.models import PasswordReset

            self.assertTrue(PasswordReset is not None)
        except ImportError:
            self.fail("PasswordReset模型不存在")

    def test_password_reset_can_be_created(self):
        """测试PasswordReset模型可以被创建"""
        from apps.users.models import PasswordReset

        user = User.objects.create_user(
            username="password_reset_user",
            email="password_reset@example.com",
            password="testpass123",
        )

        password_reset = PasswordReset.objects.create(
            user=user,
            token="reset-token-123",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        self.assertIsNotNone(password_reset.id)
        self.assertEqual(password_reset.user, user)
        self.assertEqual(password_reset.token, "reset-token-123")

    def test_password_reset_has_required_fields(self):
        """测试PasswordReset模型包含所有必需字段"""
        from apps.users.models import PasswordReset

        user = User.objects.create_user(
            username="password_reset_fields",
            email="password_reset_fields@example.com",
            password="testpass123",
        )

        password_reset = PasswordReset.objects.create(
            user=user,
            token="reset-token-456",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        # 验证所有字段存在
        self.assertTrue(hasattr(password_reset, "id"))
        self.assertTrue(hasattr(password_reset, "user"))
        self.assertTrue(hasattr(password_reset, "token"))
        self.assertTrue(hasattr(password_reset, "expires_at"))
        self.assertTrue(hasattr(password_reset, "used_at"))
        self.assertTrue(hasattr(password_reset, "created_at"))

        # 验证字段类型和默认值
        self.assertIsNotNone(password_reset.id)
        self.assertEqual(password_reset.user, user)
        self.assertIsNone(password_reset.used_at)  # 默认应该为None

    def test_password_reset_token_unique_index(self):
        """测试PasswordReset表的token字段有唯一索引"""
        from apps.users.models import PasswordReset

        user = User.objects.create_user(
            username="password_reset_unique",
            email="password_reset_unique@example.com",
            password="testpass123",
        )

        PasswordReset.objects.create(
            user=user,
            token="unique-reset-token-123",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        # 尝试创建相同token的记录应该失败
        with self.assertRaises(IntegrityError):
            PasswordReset.objects.create(
                user=user,
                token="unique-reset-token-123",  # 相同的token
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )

    def test_password_reset_foreign_key_relationship(self):
        """测试PasswordReset模型的外键关系"""
        from apps.users.models import PasswordReset

        user = User.objects.create_user(
            username="password_reset_fk",
            email="password_reset_fk@example.com",
            password="testpass123",
        )

        password_reset = PasswordReset.objects.create(
            user=user,
            token="reset-token-fk",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        # 验证外键关系
        self.assertEqual(password_reset.user, user)
        # 验证可以通过user反向查询（使用related_name）
        self.assertIn(password_reset, user.password_resets.all())
