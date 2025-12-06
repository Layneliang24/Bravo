# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-001-internal-example
"""Example视图模块单元测试"""

import pytest
from django.test import TestCase


@pytest.mark.unit
class ExampleViewsTests(TestCase):
    """Example视图单元测试"""

    def test_example_view(self):
        """测试示例视图"""
        from apps.example.views import test_view

        result = test_view(None)
        self.assertEqual(result["status"], "ok")
