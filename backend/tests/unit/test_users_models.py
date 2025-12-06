# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-INTERNAL-COMMON
"""用户模型单元测试"""

import pytest
from django.contrib.auth import get_user_model

# Django异常导入根据需要添加
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class UserModelTests(TestCase):
    """用户模型测试"""

    def test_create_user(self):
        """测试创建普通用户"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """测试创建超级用户"""
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("adminpass123"))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_string_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username="stringtest", email="string@example.com", password="stringpass123"
        )

        self.assertEqual(str(user), "stringtest")

    def test_user_email_normalization(self):
        """测试邮箱地址规范化"""
        user = User.objects.create_user(
            username="emailtest", email="Test@EXAMPLE.COM", password="emailpass123"
        )

        # Django应该自动规范化邮箱地址
        self.assertEqual(user.email, "Test@example.com")

    def test_username_uniqueness(self):
        """测试用户名唯一性约束"""
        User.objects.create_user(
            username="uniquetest", email="unique1@example.com", password="uniquepass123"
        )

        # 尝试创建相同用户名的用户应该失败
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="uniquetest",
                email="unique2@example.com",
                password="uniquepass123",
            )

    def test_user_password_hashing(self):
        """测试密码哈希功能"""
        password = "testpassword123"
        user = User.objects.create_user(
            username="hashtest", email="hash@example.com", password=password
        )

        # 密码应该被哈希，不应该以明文存储
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))

        # 但应该能通过check_password验证
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_inactive_by_default(self):
        """测试用户默认状态"""
        user = User.objects.create_user(
            username="activetest", email="active@example.com", password="activepass123"
        )

        # 用户默认应该是活跃的
        self.assertTrue(user.is_active)

    def test_user_db_table_name(self):
        """测试用户模型数据库表名"""
        # pylint: disable=protected-access
        self.assertEqual(User._meta.db_table, "users_user")

    def test_user_verbose_names(self):
        """测试用户模型显示名称"""
        # pylint: disable=protected-access
        self.assertEqual(User._meta.verbose_name, "用户")
        # pylint: disable=protected-access
        self.assertEqual(User._meta.verbose_name_plural, "用户")

    def test_user_groups_none(self):
        """测试用户groups和user_permissions字段为None"""
        user = User.objects.create_user(
            username="permtest", email="perm@example.com", password="permpass123"
        )

        # 在这个自定义User模型中，groups和user_permissions被设为None
        self.assertIsNone(user.groups)
        self.assertIsNone(user.user_permissions)

    def test_user_required_fields(self):
        """测试用户模型必需字段"""
        # 用户名是必需的
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username="", email="required@example.com", password="requiredpass123"
            )

    def test_user_without_email(self):
        """测试不提供邮箱创建用户"""
        user = User.objects.create_user(username="noemail", password="noemailpass123")

        self.assertEqual(user.username, "noemail")
        self.assertEqual(user.email, "")  # 邮箱可以为空

    def test_user_set_password(self):
        """测试设置密码功能"""
        user = User.objects.create_user(
            username="setpasstest", email="setpass@example.com", password="oldpass123"
        )

        # 验证旧密码
        self.assertTrue(user.check_password("oldpass123"))

        # 设置新密码
        user.set_password("newpass123")
        user.save()

        # 验证新密码
        self.assertTrue(user.check_password("newpass123"))
        self.assertFalse(user.check_password("oldpass123"))

    def test_user_manager_methods(self):
        """测试用户管理器方法"""
        # 测试create_user方法
        user = User.objects.create_user("manager_test", "manager@test.com", "pass123")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # 测试create_superuser方法
        superuser = User.objects.create_superuser(
            "super_manager", "super@test.com", "pass123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
