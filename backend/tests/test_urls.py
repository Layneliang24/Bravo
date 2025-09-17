# -*- coding: utf-8 -*-
"""测试用 URL 配置"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """健康检查端点"""
    _ = request  # 标记参数为故意未使用
    return JsonResponse({"status": "ok"})


def api_root(request):
    """API 根端点"""
    _ = request  # 标记参数为故意未使用
    return JsonResponse({"message": "API Root"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("api/", api_root),
]
