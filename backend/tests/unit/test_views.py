# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-001-example-demo
"""Example、Test Optimized、Test Scenario2、Test Scenario3、Test T01 视图模块单元测试"""

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


@pytest.mark.unit
class TestOptimizedViewsTests(TestCase):
    """Test Optimized视图单元测试"""

    def test_optimized_view(self):
        """测试优化视图"""
        from apps.test_optimized.views import test_view

        result = test_view(None)
        self.assertEqual(result["status"], "ok")


@pytest.mark.unit
class TestScenario2ViewsTests(TestCase):
    """Test Scenario2视图单元测试"""

    def test_scenario2_view(self):
        """测试场景2视图"""
        from apps.test_scenario2.views import scenario2_view

        result = scenario2_view(None)
        self.assertEqual(result["status"], "scenario2")


@pytest.mark.unit
class TestScenario3ViewsTests(TestCase):
    """Test Scenario3视图单元测试"""

    def test_scenario3_view(self):
        """测试场景3视图"""
        from apps.test_scenario3.views import scenario3_view

        result = scenario3_view(None)
        self.assertEqual(result["status"], "scenario3")


@pytest.mark.unit
class TestT01ViewsTests(TestCase):
    """Test T01视图单元测试"""

    def test_t01_view(self):
        """测试T01视图"""
        from apps.test_t01.views import test_view

        result = test_view()
        self.assertEqual(result["status"], "ok")
