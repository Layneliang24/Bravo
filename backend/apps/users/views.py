# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关视图"""

import secrets
from datetime import timedelta

from apps.users.models import EmailVerification, PasswordReset
from apps.users.serializers import (
    CaptchaRefreshRequestSerializer,
    CaptchaResponseSerializer,
    ErrorResponseSerializer,
    LoginResponseSerializer,
    MessageResponseSerializer,
    PasswordResetSerializer,
    PreviewLoginSerializer,
    PreviewResponseSerializer,
    RegisterResponseSerializer,
    SendEmailVerificationSerializer,
    SendPasswordResetSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)
from apps.users.tasks import send_email_verification, send_password_reset_email
from apps.users.throttling import PreviewLoginThrottle
from apps.users.utils import (
    find_user_by_email_or_username,
    generate_captcha,
    store_captcha,
)
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# 验证码过期时间（秒）
CAPTCHA_EXPIRES_IN = 300  # 5分钟


class BaseCaptchaView(APIView):
    """验证码API基类，提供公共方法"""

    permission_classes = []  # 允许匿名访问

    def _handle_captcha_error(self, errors):
        """
        处理验证码错误（公共方法）

        Args:
            errors: 序列化器错误字典

        Returns:
            Response或None: 如果是验证码错误则返回Response，否则返回None
        """
        if "captcha_answer" in errors:
            captcha_error = errors["captcha_answer"]
            if isinstance(captcha_error, list) and any(
                "验证码错误" in str(e) for e in captcha_error
            ):
                return Response(
                    {"error": "验证码错误", "code": "INVALID_CAPTCHA"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return None

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

    def _generate_tokens(self, user):
        """
        为用户生成JWT Token（公共方法）

        Args:
            user: User实例

        Returns:
            tuple: (access_token, refresh_token)
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)


class CaptchaAPIView(BaseCaptchaView):
    """获取验证码API视图"""

    @extend_schema(
        summary="获取验证码",
        description="获取图形验证码，返回验证码ID和Base64编码的图片",
        responses={
            200: CaptchaResponseSerializer,
        },
        tags=["验证码"],
    )
    def get(self, request):
        """
        获取验证码

        返回:
            Response: 包含captcha_id, captcha_image, expires_in的JSON响应
        """
        return self._create_captcha_response()


class CaptchaRefreshAPIView(BaseCaptchaView):
    """刷新验证码API视图"""

    @extend_schema(
        summary="刷新验证码",
        description="刷新验证码，可选择性删除旧验证码",
        request=CaptchaRefreshRequestSerializer,
        responses={
            200: CaptchaResponseSerializer,
        },
        tags=["验证码"],
    )
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
        # 验证请求数据（可选字段，允许空请求体）
        serializer = CaptchaRefreshRequestSerializer(data=request.data)
        if not serializer.is_valid():
            # 如果验证失败，返回400错误
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 如果提供了旧的captcha_id，删除旧的验证码（可选）
        old_captcha_id = serializer.validated_data.get("captcha_id")
        if old_captcha_id:
            # 记录删除操作，用于调试
            import logging

            logger = logging.getLogger(__name__)
            old_answer = cache.get(f"captcha:{old_captcha_id}")
            logger.info(
                f"Refreshing captcha: deleting old captcha "
                f"(old_captcha_id={old_captcha_id}, old_answer={old_answer})"
            )
            cache.delete(f"captcha:{old_captcha_id}")

        # 生成并返回新的验证码
        return self._create_captcha_response()


class CaptchaAnswerAPIView(BaseCaptchaView):
    """获取验证码答案API视图（仅测试环境）"""

    def get(self, request, captcha_id):
        """
        获取验证码答案（仅测试环境）

        参数:
            captcha_id: 验证码ID

        返回:
            Response: 包含answer的JSON响应（仅测试环境）
        """
        # 仅允许测试环境访问
        if not request.META.get("HTTP_X_TEST_ENVIRONMENT") == "true":
            return Response({"error": "此API仅用于测试环境"}, status=status.HTTP_403_FORBIDDEN)

        # 从Redis获取验证码答案
        from apps.users.utils import get_captcha_answer

        answer = get_captcha_answer(captcha_id)
        if answer is None:
            return Response({"error": "验证码不存在或已过期"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"answer": answer}, status=status.HTTP_200_OK)


class RegisterAPIView(BaseCaptchaView):
    """用户注册API视图"""

    permission_classes = []  # 允许匿名访问

    @extend_schema(
        summary="用户注册",
        description="用户注册接口，需要提供邮箱、密码和验证码",
        request=UserRegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["认证"],
    )
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

        # 生成邮箱验证token
        import secrets

        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        # 创建EmailVerification记录
        EmailVerification.objects.create(
            user=user,
            email=user.email,
            token=token,
            expires_at=expires_at,
        )

        # 调用Celery任务发送验证邮件
        send_email_verification.delay(
            user_id=user.id,
            email=user.email,
            token=token,
        )

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
                            "error": (
                                password_error[0] if password_error else "密码不符合要求"
                            ),
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


class LoginAPIView(BaseCaptchaView):
    """用户登录API视图"""

    permission_classes = []  # 允许匿名访问

    @extend_schema(
        summary="用户登录",
        description="用户登录接口，需要提供邮箱/用户名、密码和验证码",
        request=UserLoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=["认证"],
    )
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
            captcha_error_response = self._handle_captcha_error(errors)
            if captcha_error_response:
                return captcha_error_response

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
                    from apps.users.utils import find_user_by_email_or_username

                    email_or_username = request.data.get("email")
                    if email_or_username:
                        user = find_user_by_email_or_username(email_or_username)

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
                                    {
                                        "error": "账户已被锁定，请稍后再试",
                                        "code": "ACCOUNT_LOCKED",
                                    },
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
                        {
                            "error": "用户不存在或密码错误",
                            "code": "INVALID_CREDENTIALS",
                        },
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


class PreviewAPIView(BaseCaptchaView):
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

    @extend_schema(
        summary="登录预验证（获取用户头像）",
        description="登录前预验证接口，用于获取用户头像等信息，始终返回200状态码",
        request=PreviewLoginSerializer,
        responses={
            200: PreviewResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["认证"],
    )
    def post(self, request):
        serializer = PreviewLoginSerializer(data=request.data)

        if not serializer.is_valid():
            # 处理错误响应格式
            errors = serializer.errors

            # 检查验证码错误
            captcha_error_response = self._handle_captcha_error(errors)
            if captcha_error_response:
                return captcha_error_response

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


class TokenRefreshAPIView(APIView):
    """JWT Token刷新API视图"""

    permission_classes = []  # 允许匿名访问（只需要refresh token）

    @extend_schema(
        summary="刷新JWT Token",
        description="使用refresh token获取新的access token",
        request=TokenRefreshRequestSerializer,
        responses={
            200: TokenRefreshResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["认证"],
    )
    def post(self, request):
        """
        刷新JWT Token

        请求体:
            refresh: Refresh Token字符串

        返回:
            Response: 包含新的access token的JSON响应
        """
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"refresh": ["此字段是必需的。"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 验证并刷新token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            # 返回新的access token
            return Response(
                {"access": access_token},
                status=status.HTTP_200_OK,
            )

        except (TokenError, InvalidToken):
            return Response(
                {"error": "无效的refresh token", "code": "INVALID_REFRESH_TOKEN"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "Token刷新失败", "code": "REFRESH_FAILED"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(APIView):
    """用户登出API视图"""

    permission_classes = [IsAuthenticated]  # 需要认证

    @extend_schema(
        summary="用户登出",
        description="用户登出接口，需要提供JWT Token",
        responses={
            200: MessageResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["认证"],
    )
    def post(self, request):
        """
        用户登出

        请求头:
            Authorization: Bearer <access_token>

        返回:
            Response: 包含成功消息的JSON响应
        """
        # 检查是否已认证
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "未授权", "code": "UNAUTHORIZED"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # 获取refresh token（如果提供）
            refresh_token = request.data.get("refresh_token")

            if refresh_token:
                try:
                    # 将refresh token加入黑名单（如果配置了黑名单）
                    refresh = RefreshToken(refresh_token)
                    refresh.blacklist()
                except (TokenError, InvalidToken):
                    # 如果refresh token无效，忽略（不影响登出）
                    pass

            # 返回成功消息
            return Response(
                {"message": "登出成功"},
                status=status.HTTP_200_OK,
            )

        except Exception:
            # 即使出错，也返回成功（避免泄露错误信息）
            return Response(
                {"message": "登出成功"},
                status=status.HTTP_200_OK,
            )


class SendEmailVerificationAPIView(APIView):
    """发送邮箱验证邮件API视图"""

    permission_classes = [IsAuthenticated]  # 需要认证

    @extend_schema(
        summary="发送邮箱验证邮件",
        description="发送邮箱验证邮件，需要提供JWT Token和邮箱地址",
        request=SendEmailVerificationSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["邮箱验证"],
    )
    def post(self, request):
        """
        发送邮箱验证邮件

        请求头:
            Authorization: Bearer <access_token>

        请求体:
            {
                "email": "user@example.com"
            }

        返回:
            Response: 包含成功消息的JSON响应
        """
        try:
            serializer = SendEmailVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = serializer.validated_data["email"]

            # 验证邮箱是否属于当前用户
            if request.user.email != email:
                return Response(
                    {"error": "邮箱不属于当前用户", "code": "EMAIL_MISMATCH"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 生成唯一的验证token
            token = secrets.token_urlsafe(32)

            # 设置过期时间（24小时）
            expires_at = timezone.now() + timedelta(hours=24)

            # 创建或更新EmailVerification记录
            verification, created = EmailVerification.objects.update_or_create(
                user=request.user,
                email=email,
                defaults={
                    "token": token,
                    "expires_at": expires_at,
                    "verified_at": None,  # 重置验证状态
                },
            )

            # 调用Celery任务发送邮件
            send_email_verification.delay(
                user_id=request.user.id,
                email=email,
                token=token,
            )

            return Response(
                {"message": "验证邮件已发送，请查收"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 捕获所有未预期的异常
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"发送邮箱验证邮件时发生错误: user_id={request.user.id}, "
                f"email={request.data.get('email')}, error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"error": "发送验证邮件失败，请稍后重试", "code": "EMAIL_SEND_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyEmailAPIView(APIView):
    """邮箱验证API视图"""

    permission_classes = []  # 允许匿名访问（通过token验证）

    @extend_schema(
        summary="验证邮箱",
        description="通过token验证邮箱",
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["邮箱验证"],
    )
    def get(self, request, token):
        """
        验证邮箱

        URL参数:
            token: 验证令牌

        返回:
            Response: 包含成功或错误消息的JSON响应
        """
        try:
            # 查找验证记录
            try:
                verification = EmailVerification.objects.get(token=token)
            except EmailVerification.DoesNotExist:
                return Response(
                    {"error": "无效的验证令牌", "code": "INVALID_TOKEN"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 检查是否已过期
            if verification.is_expired():
                return Response(
                    {"error": "验证令牌已过期", "code": "TOKEN_EXPIRED"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 检查是否已验证
            if verification.is_verified():
                return Response(
                    {
                        "error": "该验证令牌已被使用（已验证）",
                        "code": "TOKEN_ALREADY_VERIFIED",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 验证成功，更新用户状态
            user = verification.user
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
            user.save()

            # 标记验证记录为已验证
            verification.verified_at = timezone.now()
            verification.save()

            return Response(
                {"message": "邮箱验证成功"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 捕获所有未预期的异常
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"邮箱验证时发生错误: token={token}, error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"error": "邮箱验证失败，请稍后重试", "code": "VERIFICATION_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResendEmailVerificationAPIView(APIView):
    """通过验证token重新发送邮箱验证邮件API视图"""

    permission_classes = []  # 允许匿名访问（通过token验证）

    @extend_schema(
        summary="重新发送邮箱验证邮件",
        description="通过验证token重新发送邮箱验证邮件",
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["邮箱验证"],
    )
    def post(self, request):
        """
        通过验证token重新发送邮箱验证邮件

        查询参数:
            token: 验证令牌（从URL获取）

        返回:
            Response: 包含成功消息的JSON响应
        """
        try:
            # 从查询参数获取token
            token = request.query_params.get("token")
            if not token:
                return Response(
                    {"error": "缺少验证令牌", "code": "MISSING_TOKEN"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 查找验证记录
            try:
                verification = EmailVerification.objects.get(token=token)
            except EmailVerification.DoesNotExist:
                return Response(
                    {"error": "无效的验证令牌", "code": "INVALID_TOKEN"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 检查是否已验证（已验证的不能重新发送）
            if verification.is_verified():
                return Response(
                    {"error": "该邮箱已验证，无需重新发送", "code": "ALREADY_VERIFIED"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 生成新的验证token
            new_token = secrets.token_urlsafe(32)

            # 设置过期时间（24小时）
            expires_at = timezone.now() + timedelta(hours=24)

            # 更新验证记录
            verification.token = new_token
            verification.expires_at = expires_at
            verification.verified_at = None  # 重置验证状态
            verification.save()

            # 调用Celery任务发送邮件
            send_email_verification.delay(
                user_id=verification.user.id,
                email=verification.email,
                token=new_token,
            )

            return Response(
                {"message": "验证邮件已重新发送，请查收您的邮箱"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 捕获所有未预期的异常
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"重新发送邮箱验证邮件时发生错误: "
                f"token={request.query_params.get('token')}, error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"error": "重新发送验证邮件失败，请稍后重试", "code": "RESEND_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendPasswordResetAPIView(BaseCaptchaView):
    """发送密码重置邮件API视图"""

    permission_classes = []  # 允许匿名访问

    @extend_schema(
        summary="发送密码重置邮件",
        description="发送密码重置邮件，需要提供邮箱和验证码",
        request=SendPasswordResetSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["密码重置"],
    )
    def post(self, request):
        """
        发送密码重置邮件

        请求体:
            {
                "email": "user@example.com",
                "captcha_id": "uuid",
                "captcha_answer": "A3B7"
            }

        返回:
            Response: 包含成功消息的JSON响应
        """
        try:
            serializer = SendPasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                # 处理验证码错误
                captcha_error = self._handle_captcha_error(serializer.errors)
                if captcha_error:
                    return captcha_error

                # 统一处理其他验证错误，确保所有错误都有code字段
                errors = serializer.errors
                if "email" in errors:
                    return Response(
                        {"error": "邮箱格式不正确", "code": "INVALID_EMAIL"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 其他验证错误，统一格式
                return Response(
                    {
                        "error": "请求参数验证失败",
                        "code": "VALIDATION_ERROR",
                        "details": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = serializer.validated_data["email"]

            # 查找用户（防止用户枚举攻击：无论邮箱是否存在都返回成功）
            user = find_user_by_email_or_username(email)

            # 如果用户存在，生成重置token并发送邮件
            if user:
                # 生成唯一的重置token
                token = secrets.token_urlsafe(32)

                # 设置过期时间（24小时）
                expires_at = timezone.now() + timedelta(hours=24)

                # 创建或更新PasswordReset记录
                reset, created = PasswordReset.objects.update_or_create(
                    user=user,
                    defaults={
                        "token": token,
                        "expires_at": expires_at,
                        "used_at": None,  # 重置使用状态
                    },
                )

                # 调用Celery任务发送邮件
                send_password_reset_email.delay(
                    user_id=user.id,
                    email=email,
                    token=token,
                )

            # 无论用户是否存在，都返回成功消息（防止用户枚举攻击）
            return Response(
                {"message": "密码重置邮件已发送，请查收"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 捕获所有未预期的异常
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"发送密码重置邮件时发生错误: email={request.data.get('email')}, " f"error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"error": "发送重置邮件失败，请稍后重试", "code": "EMAIL_SEND_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetAPIView(APIView):
    """重置密码API视图"""

    permission_classes = []  # 允许匿名访问（通过token验证）

    @extend_schema(
        summary="重置密码",
        description="通过重置token重置密码",
        request=PasswordResetSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=["密码重置"],
    )
    def post(self, request):
        """
        重置密码

        请求体:
            {
                "token": "reset-token",
                "password": "NewSecurePass123",
                "password_confirm": "NewSecurePass123"
            }

        返回:
            Response: 包含成功或错误消息的JSON响应
        """
        try:
            serializer = PasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                # 统一处理错误格式，确保所有错误都有code字段
                errors = serializer.errors

                # 处理密码错误
                if "password" in errors:
                    password_errors = errors["password"]
                    if isinstance(password_errors, list):
                        # 处理Django的min_length验证错误
                        for error in password_errors:
                            if "at least 8 characters" in str(error):
                                return Response(
                                    {
                                        "error": "密码长度至少为8位",
                                        "code": "WEAK_PASSWORD",
                                    },
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                    elif (
                        isinstance(password_errors, dict) and "error" in password_errors
                    ):
                        # 处理自定义验证错误，确保有code字段
                        error_response = password_errors.copy()
                        if "code" not in error_response:
                            error_response["code"] = "WEAK_PASSWORD"
                        return Response(
                            error_response,
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                # 处理token错误
                if "token" in errors:
                    return Response(
                        {"error": "重置令牌不能为空", "code": "TOKEN_REQUIRED"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 处理密码确认错误
                if "password_confirm" in errors or "non_field_errors" in errors:
                    mismatch_error = errors.get("password_confirm") or errors.get(
                        "non_field_errors"
                    )
                    if isinstance(mismatch_error, list) and any(
                        "密码" in str(e) and "不一致" in str(e) for e in mismatch_error
                    ):
                        return Response(
                            {
                                "error": "密码和确认密码不一致",
                                "code": "PASSWORD_MISMATCH",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                # 其他验证错误，统一格式
                return Response(
                    {
                        "error": "请求参数验证失败",
                        "code": "VALIDATION_ERROR",
                        "details": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["password"]

            # 查找重置记录
            try:
                reset = PasswordReset.objects.get(token=token)
            except PasswordReset.DoesNotExist:
                return Response(
                    {"error": "无效的重置令牌", "code": "INVALID_TOKEN"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 检查是否已过期
            if reset.is_expired():
                return Response(
                    {"error": "重置令牌已过期", "code": "TOKEN_EXPIRED"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 检查是否已使用
            if reset.is_used():
                return Response(
                    {"error": "该重置令牌已被使用", "code": "TOKEN_ALREADY_USED"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 重置密码成功，更新用户密码
            user = reset.user
            user.set_password(new_password)
            user.save()

            # 标记重置记录为已使用
            reset.used_at = timezone.now()
            reset.save()

            return Response(
                {"message": "密码重置成功，请使用新密码登录"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 捕获所有未预期的异常
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"重置密码时发生错误: token={request.data.get('token')}, error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"error": "密码重置失败，请稍后重试", "code": "RESET_FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
