# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-002-internal-test
"""Test Optimized视图模块单元测试"""

import pytest
from django.test import TestCase


@pytest.mark.unit
class TestOptimizedViewsTests(TestCase):
    """Test Optimized视图单元测试"""

    def test_optimized_view(self):
        """测试优化视图"""
        from apps.test_optimized.views import test_view

        result = test_view(None)
        self.assertEqual(result["status"], "ok")
