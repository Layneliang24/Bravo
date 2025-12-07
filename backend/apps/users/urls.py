# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关URL路由"""

from apps.users.views import CaptchaAPIView, CaptchaRefreshAPIView
from django.urls import path

app_name = "users"

urlpatterns = [
    path("captcha/", CaptchaAPIView.as_view(), name="captcha"),
    path("captcha/refresh/", CaptchaRefreshAPIView.as_view(), name="captcha-refresh"),
]
