# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关序列化器"""

import re

from apps.users.utils import verify_captcha
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.Serializer):
    """用户注册序列化器"""

    email = serializers.EmailField(required=True, help_text="用户邮箱地址")
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="用户密码，最少8位，包含字母和数字",
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        help_text="确认密码，必须与password一致",
    )
    captcha_id = serializers.CharField(required=True, help_text="验证码ID")
    captcha_answer = serializers.CharField(required=True, help_text="验证码答案")

    def validate_email(self, value):
        """验证邮箱唯一性"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "该邮箱已被注册", "code": "EMAIL_EXISTS"}
            )
        return value

    def validate_password(self, value):
        """验证密码强度"""
        # 最少8位
        if len(value) < 8:
            raise serializers.ValidationError("密码长度至少为8位")

        # 必须包含字母和数字
        has_letter = bool(re.search(r"[a-zA-Z]", value))
        has_digit = bool(re.search(r"\d", value))

        if not (has_letter and has_digit):
            raise serializers.ValidationError(
                {"error": "密码必须包含字母和数字", "code": "WEAK_PASSWORD"}
            )

        # 使用Django内置密码验证器
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    def validate(self, attrs):
        """验证密码确认和验证码"""
        # 验证密码和确认密码是否一致
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"error": "密码和确认密码不一致", "code": "PASSWORD_MISMATCH"}
            )

        # 验证验证码
        captcha_id = attrs.get("captcha_id")
        captcha_answer = attrs.get("captcha_answer")

        if not verify_captcha(captcha_id, captcha_answer):
            raise serializers.ValidationError(
                {"captcha_answer": "验证码错误"}, code="INVALID_CAPTCHA"
            )

        return attrs

    def create(self, validated_data):
        """创建用户"""
        email = validated_data["email"]
        password = validated_data["password"]

        # 使用email作为username（如果username字段需要）
        # 或者生成一个基于email的username
        username = email.split("@")[0]  # 使用邮箱前缀作为username

        # 确保username唯一
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_email_verified=False,  # 注册时邮箱未验证
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""

    email = serializers.CharField(
        required=True, help_text="用户邮箱或用户名"
    )  # 使用CharField支持邮箱和用户名
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="用户密码",
    )
    captcha_id = serializers.CharField(required=True, help_text="验证码ID")
    captcha_answer = serializers.CharField(required=True, help_text="验证码答案")

    def validate(self, attrs):
        """验证验证码和用户认证"""
        # 验证验证码
        captcha_id = attrs.get("captcha_id")
        captcha_answer = attrs.get("captcha_answer")

        if not verify_captcha(captcha_id, captcha_answer):
            raise serializers.ValidationError(
                {"captcha_answer": "验证码错误"}, code="INVALID_CAPTCHA"
            )

        # 验证用户和密码
        email_or_username = attrs.get("email")
        password = attrs.get("password")

        # 尝试通过邮箱或用户名查找用户
        user = None
        if "@" in email_or_username:
            # 通过邮箱查找
            try:
                user = User.objects.get(email=email_or_username)
            except User.DoesNotExist:
                pass
        else:
            # 通过用户名查找
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError(
                {"error": "用户不存在或密码错误", "code": "INVALID_CREDENTIALS"}
            )

        # 验证密码
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"error": "用户不存在或密码错误", "code": "INVALID_CREDENTIALS"}
            )

        # 将用户对象添加到validated_data中，供视图使用
        attrs["user"] = user
        return attrs
