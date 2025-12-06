# -*- coding: utf-8 -*-
"""测试环境URL配置 - 简化版本，不依赖外部包"""

from apps.common.views import api_info, health_check
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home_view(_request):
    """测试环境根路径视图，返回API信息"""
    return JsonResponse(
        {
            "message": "Welcome to Bravo API (Test)",
            "version": "1.0.0",
            "endpoints": {
                "api_docs": "/api/docs/",
                "admin": "/admin/",
                "health": "/health/",
                "api_info": "/api-info/",
            },
        }
    )


urlpatterns = [
    # 根路径
    path("", home_view, name="home"),
    # 管理后台
    path("admin/", admin.site.urls),
    # 健康检查和API信息
    path("health/", health_check, name="health_check"),
    path("api-info/", api_info, name="api_info"),
    # 通用应用URL (使用common/前缀避免与根路径冲突)
    path("common/", include("apps.common.urls")),
]
