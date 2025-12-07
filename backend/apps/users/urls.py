# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关URL路由"""

from apps.users.views import (
    CaptchaAPIView,
    CaptchaRefreshAPIView,
    LoginAPIView,
    LogoutAPIView,
    PreviewAPIView,
    RegisterAPIView,
    SendEmailVerificationAPIView,
    TokenRefreshAPIView,
)
from django.urls import path

app_name = "users"

urlpatterns = [
    path("captcha/", CaptchaAPIView.as_view(), name="captcha"),
    path("captcha/refresh/", CaptchaRefreshAPIView.as_view(), name="captcha-refresh"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("preview/", PreviewAPIView.as_view(), name="preview"),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "email/verify/send/",
        SendEmailVerificationAPIView.as_view(),
        name="email-verify-send",
    ),
]
