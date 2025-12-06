# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-005-internal-test-t01
"""Test T01视图模块单元测试"""

import pytest
from django.test import TestCase


@pytest.mark.unit
class TestT01ViewsTests(TestCase):
    """Test T01视图单元测试"""

    def test_t01_view(self):
        """测试T01视图"""
        from apps.test_t01.views import test_view

        result = test_view()
        self.assertEqual(result["status"], "ok")
