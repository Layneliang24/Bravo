# -*- coding: utf-8 -*-
"""测试环境URL配置 - 简化版本，不依赖外部包"""

from django.contrib import admin
from django.urls import path, include
from apps.common.views import health_check_view, api_info_view

urlpatterns = [
    # 管理后台
    path("admin/", admin.site.urls),
    
    # 健康检查和API信息
    path("health/", health_check_view, name="health_check"),
    path("api-info/", api_info_view, name="api_info"),
    
    # 通用应用URL
    path("", include("apps.common.urls")),
]
