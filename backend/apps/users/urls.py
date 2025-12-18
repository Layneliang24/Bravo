# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关URL路由"""

from apps.users.views import (
    CaptchaAnswerAPIView,
    CaptchaAPIView,
    CaptchaRefreshAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetAPIView,
    PreviewAPIView,
    RegisterAPIView,
    ResendEmailVerificationAPIView,
    SendEmailVerificationAPIView,
    SendPasswordResetAPIView,
    TokenRefreshAPIView,
    VerifyEmailAPIView,
)
from django.urls import path

app_name = "users"

urlpatterns = [
    path("captcha/", CaptchaAPIView.as_view(), name="captcha"),
    path("captcha/refresh/", CaptchaRefreshAPIView.as_view(), name="captcha-refresh"),
    path(
        "captcha/<str:captcha_id>/answer/",
        CaptchaAnswerAPIView.as_view(),
        name="captcha-answer",
    ),
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
    path(
        "email/verify/<str:token>/",
        VerifyEmailAPIView.as_view(),
        name="email-verify",
    ),
    path(
        "email/verify/resend/",
        ResendEmailVerificationAPIView.as_view(),
        name="email-verify-resend",
    ),
    path(
        "password/reset/send/",
        SendPasswordResetAPIView.as_view(),
        name="password-reset-send",
    ),
    path(
        "password/reset/",
        PasswordResetAPIView.as_view(),
        name="password-reset",
    ),
]
