# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关视图"""

from apps.users.utils import generate_captcha, store_captcha
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CaptchaAPIView(APIView):
    """获取验证码API视图"""

    permission_classes = []  # 允许匿名访问

    def get(self, request):
        """
        获取验证码

        返回:
            Response: 包含captcha_id, captcha_image, expires_in的JSON响应
        """
        # 生成验证码
        captcha_id, captcha_image, answer = generate_captcha()

        # 存储验证码答案到Redis（5分钟过期）
        store_captcha(captcha_id, answer, expires_in=300)

        # 返回响应
        return Response(
            {
                "captcha_id": captcha_id,
                "captcha_image": captcha_image,
                "expires_in": 300,
            },
            status=status.HTTP_200_OK,
        )


class CaptchaRefreshAPIView(APIView):
    """刷新验证码API视图"""

    permission_classes = []  # 允许匿名访问

    def post(self, request):
        """
        刷新验证码

        请求体:
            {
                "captcha_id": "uuid"  # 可选的旧验证码ID
            }

        返回:
            Response: 包含新的captcha_id, captcha_image, expires_in的JSON响应
        """
        # 生成新的验证码
        captcha_id, captcha_image, answer = generate_captcha()

        # 存储验证码答案到Redis（5分钟过期）
        store_captcha(captcha_id, answer, expires_in=300)

        # 返回响应
        return Response(
            {
                "captcha_id": captcha_id,
                "captcha_image": captcha_image,
                "expires_in": 300,
            },
            status=status.HTTP_200_OK,
        )
