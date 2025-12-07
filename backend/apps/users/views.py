# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关视图"""

from apps.users.utils import generate_captcha, store_captcha
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# 验证码过期时间（秒）
CAPTCHA_EXPIRES_IN = 300  # 5分钟


class BaseCaptchaView(APIView):
    """验证码API基类，提供公共方法"""

    permission_classes = []  # 允许匿名访问

    def _create_captcha_response(self):
        """
        创建验证码响应（公共方法）

        返回:
            Response: 包含captcha_id, captcha_image, expires_in的JSON响应
        """
        # 生成验证码
        captcha_id, captcha_image, answer = generate_captcha()

        # 存储验证码答案到Redis
        store_captcha(captcha_id, answer, expires_in=CAPTCHA_EXPIRES_IN)

        # 返回响应
        return Response(
            {
                "captcha_id": captcha_id,
                "captcha_image": captcha_image,
                "expires_in": CAPTCHA_EXPIRES_IN,
            },
            status=status.HTTP_200_OK,
        )


class CaptchaAPIView(BaseCaptchaView):
    """获取验证码API视图"""

    def get(self, request):
        """
        获取验证码

        返回:
            Response: 包含captcha_id, captcha_image, expires_in的JSON响应
        """
        return self._create_captcha_response()


class CaptchaRefreshAPIView(BaseCaptchaView):
    """刷新验证码API视图"""

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
        # 如果提供了旧的captcha_id，删除旧的验证码（可选）
        old_captcha_id = request.data.get("captcha_id")
        if old_captcha_id:
            cache.delete(f"captcha:{old_captcha_id}")

        # 生成并返回新的验证码
        return self._create_captcha_response()
