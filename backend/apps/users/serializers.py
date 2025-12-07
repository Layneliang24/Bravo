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
            raise serializers.ValidationError("该邮箱已被注册")
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
            raise serializers.ValidationError("密码必须包含字母和数字")

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
            raise serializers.ValidationError({"password_confirm": "密码和确认密码不一致"})

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
