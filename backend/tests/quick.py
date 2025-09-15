# -*- coding: utf-8 -*-
"""
快速烟雾测试模块 - 用于合并后快速验证
包含最关键的功能测试，确保基本系统完整性
"""

import pytest

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


@pytest.mark.quick
class QuickSmokeTests(TestCase):
    """快速烟雾测试 - 验证核心功能"""

    def setUp(self):
        """设置测试环境"""
        self.client = Client()

    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)

    def test_admin_access(self):
        """测试管理界面访问"""
        response = self.client.get("/admin/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_api_root_access(self):
        """测试API根路径"""
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

    def test_database_connectivity(self):
        """测试数据库连接"""
        # 尝试创建用户来验证数据库连接
        user_count_before = User.objects.count()
        test_user = User.objects.create_user(
            username="smoke_test_user", email="smoke@test.com", password="testpass123"
        )
        self.assertIsNotNone(test_user.id)
        self.assertEqual(User.objects.count(), user_count_before + 1)

        # 清理测试数据
        test_user.delete()
