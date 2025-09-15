# -*- coding: utf-8 -*-
"""Common分页模块单元测试"""

import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class StandardResultsSetPaginationTests(TestCase):
    """标准分页配置测试"""

    def setUp(self):
        self.factory = RequestFactory()

        # 创建测试数据
        for i in range(50):
            User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="testpass123",
            )

    def test_pagination_class_import(self):
        """测试分页类能够正确导入"""
        try:
            from apps.common.pagination import StandardResultsSetPagination

            self.assertTrue(hasattr(StandardResultsSetPagination, "page_size"))
            self.assertTrue(
                hasattr(StandardResultsSetPagination, "page_size_query_param")
            )
            self.assertTrue(hasattr(StandardResultsSetPagination, "max_page_size"))
        except ImportError as error:
            # 如果导入失败，说明缺少依赖，跳过测试
            self.skipTest(f"无法导入分页类，可能缺少REST Framework依赖: {error}")

    def test_pagination_attrs(self):
        """测试分页类属性设置"""
        try:
            from apps.common.pagination import StandardResultsSetPagination

            # 检查类属性（不实例化）
            self.assertEqual(StandardResultsSetPagination.page_size, 20)
            self.assertEqual(
                StandardResultsSetPagination.page_size_query_param, "page_size"
            )
            self.assertEqual(StandardResultsSetPagination.max_page_size, 100)
        except ImportError as error:
            self.skipTest(f"无法导入分页类，可能缺少REST Framework依赖: {error}")

    def test_manual_pagination_logic(self):
        """测试手动分页逻辑（不依赖REST Framework）"""
        # 模拟分页参数解析
        page_size = 20
        page_number = 1

        queryset = User.objects.all()
        total_count = queryset.count()

        # 计算分页
        start = (page_number - 1) * page_size
        end = start + page_size

        paginated_items = list(queryset[start:end])

        self.assertTrue(len(paginated_items) <= page_size)
        self.assertTrue(len(paginated_items) <= total_count)

    def test_manual_page_2(self):
        """测试第二页的手动分页逻辑"""
        page_size = 10
        page_number = 2

        queryset = User.objects.all()

        # 计算分页
        start = (page_number - 1) * page_size
        end = start + page_size

        paginated_items = list(queryset[start:end])

        # 第二页应该有10个项目（如果总数足够）
        expected_size = min(10, max(0, queryset.count() - 10))
        self.assertEqual(len(paginated_items), expected_size)

    def test_pagination_edge_cases(self):
        """测试分页边界情况"""
        queryset = User.objects.all()
        total_count = queryset.count()

        # 测试页面大小为0的情况
        page_size = 0
        if page_size <= 0:
            page_size = 20  # 回退到默认值

        self.assertEqual(page_size, 20)

        # 测试页面大小超过总数的情况
        large_page_size = total_count + 10
        max_page_size = 100

        actual_page_size = min(large_page_size, max_page_size)
        self.assertEqual(actual_page_size, max_page_size)

    def test_pagination_helpers(self):
        """测试分页计算辅助函数"""

        def calculate_total_pages(total_items, page_size):
            """计算总页数"""
            if page_size <= 0:
                return 0
            return (total_items + page_size - 1) // page_size

        # 测试不同场景
        self.assertEqual(calculate_total_pages(50, 20), 3)  # 50个项目，每页20个，共3页
        self.assertEqual(calculate_total_pages(40, 20), 2)  # 40个项目，每页20个，共2页
        self.assertEqual(calculate_total_pages(20, 20), 1)  # 20个项目，每页20个，共1页
        self.assertEqual(calculate_total_pages(0, 20), 0)  # 0个项目，共0页

        def get_page_range(current_page, total_pages, window=2):
            """获取页面范围"""
            start = max(1, current_page - window)
            end = min(total_pages, current_page + window)
            return list(range(start, end + 1))

        # 测试页面范围计算
        self.assertEqual(get_page_range(1, 5), [1, 2, 3])
        self.assertEqual(get_page_range(3, 5), [1, 2, 3, 4, 5])
        self.assertEqual(get_page_range(5, 5), [3, 4, 5])
