# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关视图"""

from datetime import timedelta

from apps.users.serializers import (
    PreviewLoginSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)
from apps.users.throttling import PreviewLoginThrottle
from apps.users.utils import generate_captcha, store_captcha
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

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


class LoginAPIView(APIView):
    """用户登录API视图"""

    permission_classes = []  # 允许匿名访问

    def post(self, request):
        """
        用户登录

        请求体:
            {
                "email": "user@example.com" 或 "username",
                "password": "SecurePass123",
                "captcha_id": "uuid",
                "captcha_answer": "A3B7"
            }

        返回:
            Response: 包含user信息、token、refresh_token的JSON响应
        """
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            # 处理错误响应格式
            errors = serializer.errors

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

            # 检查认证错误（密码错误或用户不存在）
            if "error" in errors:
                error_data = errors["error"]
                is_credential_error = False
                if isinstance(error_data, list) and any(
                    "用户不存在" in str(e) or "密码错误" in str(e) for e in error_data
                ):
                    is_credential_error = True
                elif isinstance(error_data, dict) and "error" in error_data:
                    error_msg = error_data.get("error", "")
                    if "用户不存在" in error_msg or "密码错误" in error_msg:
                        is_credential_error = True

                # 如果是密码错误，处理失败次数
                if is_credential_error:
                    # 尝试从序列化器的validated_data中获取用户（如果存在）
                    # 注意：如果验证失败，validated_data可能为空，需要手动查找用户
                    email_or_username = request.data.get("email")
                    if email_or_username:
                        user = None
                        if "@" in email_or_username:
                            try:
                                user = User.objects.get(email=email_or_username)
                            except User.DoesNotExist:
                                pass
                        else:
                            try:
                                user = User.objects.get(username=email_or_username)
                            except User.DoesNotExist:
                                pass

                        if user:
                            # 增加失败次数
                            user.failed_login_attempts += 1
                            # 如果失败次数达到5次，锁定账户10分钟
                            if user.failed_login_attempts >= 5:
                                user.locked_until = timezone.now() + timedelta(
                                    minutes=10
                                )
                                user.save(
                                    update_fields=[
                                        "failed_login_attempts",
                                        "locked_until",
                                    ]
                                )
                                # 返回账户锁定错误
                                return Response(
                                    {"error": "账户已被锁定，请稍后再试", "code": "ACCOUNT_LOCKED"},
                                    status=status.HTTP_403_FORBIDDEN,
                                )
                            else:
                                user.save(
                                    update_fields=[
                                        "failed_login_attempts",
                                        "locked_until",
                                    ]
                                )

                    return Response(
                        {"error": "用户不存在或密码错误", "code": "INVALID_CREDENTIALS"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 如果是字典格式的其他错误
                if isinstance(error_data, dict) and "error" in error_data:
                    return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

            # 其他错误直接返回
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 获取验证后的用户对象
        user = serializer.validated_data["user"]

        # 检查账户是否被锁定（如果锁定已过期，自动解锁）
        if user.is_locked():
            return Response(
                {"error": "账户已被锁定，请稍后再试", "code": "ACCOUNT_LOCKED"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # 如果锁定已过期，清除锁定状态
        elif user.locked_until is not None and timezone.now() >= user.locked_until:
            user.locked_until = None
            user.failed_login_attempts = 0
            user.save(update_fields=["locked_until", "failed_login_attempts"])

        # 检查邮箱是否已验证
        if not user.is_email_verified:
            return Response(
                {"error": "邮箱未验证，请先验证邮箱", "code": "EMAIL_NOT_VERIFIED"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 成功登录，重置失败次数和锁定时间
        if user.failed_login_attempts > 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save(update_fields=["failed_login_attempts", "locked_until"])

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
            },
            status=status.HTTP_200_OK,
        )

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


class PreviewAPIView(APIView):
    """登录预验证API视图（用于获取用户头像）"""

    permission_classes = []  # 允许匿名访问
    throttle_classes = [PreviewLoginThrottle]  # 频率限制：每分钟10次

    def _get_avatar_letter(self, user):
        """
        获取用户头像首字母

        Args:
            user: User实例

        Returns:
            str: 首字母（优先使用display_name，否则使用username）
        """
        if user.display_name:
            # 使用display_name的首字符
            return user.display_name[0].upper()
        else:
            # 使用username的首字符
            return user.username[0].upper() if user.username else "?"

    def _format_user_preview_data(self, user):
        """
        格式化用户预览数据

        Args:
            user: User实例

        Returns:
            dict: 用户预览数据
        """
        if user.avatar:
            # 有头像
            return {
                "display_name": user.display_name or user.username,
                "avatar_url": user.avatar,
                "default_avatar": False,
            }
        else:
            # 无头像，返回默认头像信息
            return {
                "display_name": user.display_name or user.username,
                "avatar_url": None,
                "default_avatar": True,
                "avatar_letter": self._get_avatar_letter(user),
            }

    def post(self, request):
        """
        登录预验证（获取用户头像）

        请求体:
            {
                "email": "user@example.com" 或 "username",
                "password": "SecurePass123",
                "captcha_id": "uuid",
                "captcha_answer": "A3B7"
            }

        返回:
            Response: 包含valid和user信息的JSON响应（始终返回200状态码）
        """
        serializer = PreviewLoginSerializer(data=request.data)

        if not serializer.is_valid():
            # 处理错误响应格式
            errors = serializer.errors

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

            # 其他错误直接返回
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 获取验证结果
        validated_data = serializer.validated_data
        is_valid = validated_data.get("valid", False)
        user = validated_data.get("user")

        if not is_valid or user is None:
            # 账号密码错误，返回valid: false（安全考虑，不返回详细错误）
            return Response(
                {"valid": False, "user": None},
                status=status.HTTP_200_OK,
            )

        # 账号密码正确，返回用户信息
        user_data = self._format_user_preview_data(user)

        return Response(
            {"valid": True, "user": user_data},
            status=status.HTTP_200_OK,
        )
