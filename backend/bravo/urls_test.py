# -*- coding: utf-8 -*-
"""测试环境URL配置 - 简化版本，不依赖外部包"""

from django.contrib import admin
from django.urls import include, path

from apps.common.views import api_info, health_check

urlpatterns = [
    # 管理后台
    path("admin/", admin.site.urls),
    # 健康检查和API信息
    path("health/", health_check, name="health_check"),
    path("api-info/", api_info, name="api_info"),
    # 通用应用URL
    path("", include("apps.common.urls")),
]
