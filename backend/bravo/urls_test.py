# -*- coding: utf-8 -*-
"""测试环境URL配置 - 简化版本，不依赖外部包"""

from apps.common.views import api_info, health_check
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False


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
    # 用户认证相关API
    path("api/auth/", include("apps.users.urls")),
    # 通用API
    path("api/common/", include("apps.common.urls")),
    # 功能开关API
    path("api/feature-flags/", include("apps.feature_flags.urls")),
    # 其他app的URLs（目前为空，保留以便将来扩展）
    # path("api/blog/", include("apps.blog.urls")),  # 博客API（待实现）
    # path("api/english/", include("apps.english.urls")),  # 英语学习API（待实现）
    # path("api/jobs/", include("apps.jobs.urls")),  # 工作API（待实现）
]

# 如果drf-spectacular可用，添加API文档路由
if SPECTACULAR_AVAILABLE:
    urlpatterns += [
        # API文档路由
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
