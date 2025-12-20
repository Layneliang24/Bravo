"""bravo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import datetime

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health_check(request):
    """健康检查端点"""
    return JsonResponse(
        {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected",
                "cache": "connected",
            },
        }
    )


def api_root(request):
    """API根端点"""
    return JsonResponse(
        {
            "message": "Welcome to Bravo API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health/",
                "admin": "/admin/",
                "api": "/api/",
            },
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("api/", api_root, name="api-root"),
    path("api/auth/", include("apps.users.urls")),  # 用户认证相关API
    path("api/common/", include("apps.common.urls")),  # 通用API
    path("api/feature-flags/", include("apps.feature_flags.urls")),  # 功能开关API
    # 其他app的URLs（目前为空，保留以便将来扩展）
    # path("api/blog/", include("apps.blog.urls")),  # 博客API（待实现）
    # path("api/english/", include("apps.english.urls")),  # 英语学习API（待实现）
    # path("api/jobs/", include("apps.jobs.urls")),  # 工作API（待实现）
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
    # 在这里添加其他app的URLs
    # path('api/v1/', include('your_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
