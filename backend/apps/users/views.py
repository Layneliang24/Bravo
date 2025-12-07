# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关视图"""

from apps.users.serializers import UserRegisterSerializer
from apps.users.utils import generate_captcha, store_captcha
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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


class RegisterAPIView(APIView):
    """用户注册API视图"""

    permission_classes = []  # 允许匿名访问

    def _format_error_response(self, errors):
        """
        格式化错误响应，统一错误格式为 {error: str, code: str}

        Args:
            errors: DRF序列化器错误字典

        Returns:
            Response: 格式化的错误响应，如果无法格式化则返回None
        """
        # 检查验证码错误
        if "captcha_answer" in errors:
            captcha_error = errors["captcha_answer"]
            if isinstance(captcha_error, list) and any(
                "验证码错误" in str(e) for e in captcha_error
            ):
                return Response(
                    {"error": "验证码错误", "code": "INVALID_CAPTCHA"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 检查邮箱错误
        if "email" in errors:
            email_error = errors["email"]
            if isinstance(email_error, list) and any(
                "该邮箱已被注册" in str(e) for e in email_error
            ):
                return Response(
                    {"error": "该邮箱已被注册", "code": "EMAIL_EXISTS"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if isinstance(email_error, dict) and "error" in email_error:
                return Response(email_error, status=status.HTTP_400_BAD_REQUEST)

        # 检查密码错误
        if "password" in errors:
            password_error = errors["password"]
            if isinstance(password_error, list):
                if any(
                    "至少" in str(e)
                    or "Ensure this field has at least" in str(e)
                    or "密码必须" in str(e)
                    or "密码长度" in str(e)
                    for e in password_error
                ):
                    return Response(
                        {
                            "error": password_error[0] if password_error else "密码不符合要求",
                            "code": "WEAK_PASSWORD",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if isinstance(password_error, dict) and "error" in password_error:
                return Response(password_error, status=status.HTTP_400_BAD_REQUEST)

        # 检查密码不匹配错误
        if "password_confirm" in errors or "non_field_errors" in errors:
            mismatch_error = errors.get("password_confirm") or errors.get(
                "non_field_errors"
            )
            if isinstance(mismatch_error, list) and any(
                "密码" in str(e) and "不一致" in str(e) for e in mismatch_error
            ):
                return Response(
                    {"error": "密码和确认密码不一致", "code": "PASSWORD_MISMATCH"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if isinstance(mismatch_error, dict) and "error" in mismatch_error:
                return Response(mismatch_error, status=status.HTTP_400_BAD_REQUEST)

        return None

    def _generate_tokens(self, user):
        """
        为用户生成JWT Token

        Args:
            user: User实例

        Returns:
            tuple: (access_token, refresh_token)
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    def post(self, request):
        """
        用户注册

        请求体:
            {
                "email": "user@example.com",
                "password": "SecurePass123",
                "password_confirm": "SecurePass123",
                "captcha_id": "uuid",
                "captcha_answer": "A3B7"
            }

        返回:
            Response: 包含user信息、token、refresh_token和message的JSON响应
        """
        serializer = UserRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            # 尝试格式化错误响应
            formatted_response = self._format_error_response(serializer.errors)
            if formatted_response:
                return formatted_response

            # 如果无法格式化，直接返回原始错误
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户
        user = serializer.save()

        # 生成JWT Token
        access_token, refresh_token = self._generate_tokens(user)

        # 返回响应
        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "is_email_verified": user.is_email_verified,
                },
                "token": access_token,
                "refresh_token": refresh_token,
                "message": "注册成功，请查收验证邮件",
            },
            status=status.HTTP_201_CREATED,
        )
