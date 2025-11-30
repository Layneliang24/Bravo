# -*- coding: utf-8 -*-
"""Common视图模块单元测试"""

import json

import pytest
from apps.common.views import api_info, health_check
from django.test import Client, TestCase

# URL导入根据需要添加


@pytest.mark.unit
class CommonViewsTests(TestCase):
    """通用视图单元测试"""

    def setUp(self):
        self.client = Client()

    def test_health_check_get_request(self):
        """测试健康检查GET请求"""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["message"], "Bravo API is running")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("timestamp", data)

    def test_health_check_post_request(self):
        """测试健康检查POST请求"""
        response = self.client.post("/health/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["status"], "healthy")

    def test_health_check_options(self):
        """测试健康检查OPTIONS请求（CORS预检）"""
        response = self.client.options("/health/")
        self.assertEqual(response.status_code, 200)

        # 检查CORS头
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["Access-Control-Allow-Methods"], "GET, POST, OPTIONS")
        self.assertEqual(
            response["Access-Control-Allow-Headers"], "Content-Type, Authorization"
        )

    def test_health_check_cors_headers(self):
        """测试健康检查CORS头设置"""
        response = self.client.get("/health/")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_api_info_get_request(self):
        """测试API信息GET请求"""
        response = self.client.get("/api-info/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["name"], "Bravo API")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["description"], "Bravo项目后端API服务")

        # 检查端点配置
        endpoints = data["endpoints"]
        self.assertEqual(endpoints["health"], "/health/")
        self.assertEqual(endpoints["api_info"], "/api/info/")
        self.assertEqual(endpoints["blog"], "/api/v1/blog/")
        self.assertEqual(endpoints["users"], "/api/v1/auth/")

    def test_api_info_post_request(self):
        """测试API信息POST请求"""
        response = self.client.post("/api-info/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["name"], "Bravo API")

    def test_api_info_options_request(self):
        """测试API信息OPTIONS请求（CORS预检）"""
        response = self.client.options("/api-info/")
        self.assertEqual(response.status_code, 200)

        # 检查CORS头
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["Access-Control-Allow-Methods"], "GET, POST, OPTIONS")
        self.assertEqual(
            response["Access-Control-Allow-Headers"], "Content-Type, Authorization"
        )

    def test_api_info_cors_headers(self):
        """测试API信息CORS头设置"""
        response = self.client.get("/api-info/")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_health_check_direct(self):
        """直接测试health_check函数"""
        from django.http import HttpRequest

        request = HttpRequest()
        request.method = "GET"

        response = health_check(request)
        self.assertEqual(response.status_code, 200)

    def test_api_info_function_direct(self):
        """直接测试api_info函数"""
        from django.http import HttpRequest

        request = HttpRequest()
        request.method = "GET"

        response = api_info(request)
        self.assertEqual(response.status_code, 200)
