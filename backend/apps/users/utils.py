# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户相关工具函数"""

import base64
import io
import random
import string
import uuid

from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont


def generate_captcha():
    """
    生成图形验证码

    返回:
        tuple: (captcha_id, captcha_image_base64, answer)
        - captcha_id: UUID格式的验证码ID
        - captcha_image_base64: Base64编码的PNG图片（data:image/png;base64,...格式）
        - answer: 4位数字+字母混合的验证码答案
    """
    # 生成4位验证码答案（数字+字母混合）
    # 注意：验证码生成不需要密码学级别的随机数，使用random模块即可
    characters = string.ascii_uppercase + string.digits
    answer = "".join(random.choice(characters) for _ in range(4))  # nosec B311

    # 创建图片（120x40像素）
    width, height = 120, 40
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        # 尝试使用DejaVu Sans字体（Linux常见字体）
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
    except (OSError, IOError):
        try:
            # 尝试使用Arial字体（Windows常见字体）
            font = ImageFont.truetype("arial.ttf", 24)
        except (OSError, IOError):
            # 使用默认字体
            font = ImageFont.load_default()

    # 绘制验证码文字
    text_x = 10
    text_y = 8
    for char in answer:
        # 随机颜色（深色，确保在白色背景上可见）
        # 注意：验证码图片生成不需要密码学级别的随机数
        color = (
            random.randint(0, 100),  # nosec B311
            random.randint(0, 100),  # nosec B311
            random.randint(0, 100),  # nosec B311
        )
        # 随机位置偏移（增加识别难度）
        offset_x = random.randint(-2, 2)  # nosec B311
        offset_y = random.randint(-2, 2)  # nosec B311
        draw.text(
            (text_x + offset_x, text_y + offset_y),
            char,
            fill=color,
            font=font,
        )
        text_x += 25

    # 添加干扰线
    for _ in range(3):
        start_x = random.randint(0, width)  # nosec B311
        start_y = random.randint(0, height)  # nosec B311
        end_x = random.randint(0, width)  # nosec B311
        end_y = random.randint(0, height)  # nosec B311
        line_color = (
            random.randint(150, 200),  # nosec B311
            random.randint(150, 200),  # nosec B311
            random.randint(150, 200),  # nosec B311
        )
        draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=1)

    # 添加噪点
    for _ in range(50):
        x = random.randint(0, width)  # nosec B311
        y = random.randint(0, height)  # nosec B311
        noise_color = (
            random.randint(100, 200),  # nosec B311
            random.randint(100, 200),  # nosec B311
            random.randint(100, 200),  # nosec B311
        )
        draw.point((x, y), fill=noise_color)

    # 转换为Base64编码
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    captcha_image = f"data:image/png;base64,{image_base64}"

    # 生成UUID格式的验证码ID
    captcha_id = str(uuid.uuid4())

    return captcha_id, captcha_image, answer


def store_captcha(captcha_id: str, answer: str, expires_in: int = 300):
    """
    将验证码答案存储到Redis中

    参数:
        captcha_id: 验证码ID
        answer: 验证码答案
        expires_in: 过期时间（秒），默认300秒（5分钟）

    返回:
        bool: 存储是否成功
    """
    key = f"captcha:{captcha_id}"
    cache.set(key, answer, timeout=expires_in)
    return True


def verify_captcha(captcha_id: str, answer: str) -> bool:
    """
    验证验证码答案是否正确

    参数:
        captcha_id: 验证码ID
        answer: 用户输入的验证码答案

    返回:
        bool: 验证是否成功（验证成功后会自动删除验证码，防止重复使用）
    """
    if not captcha_id or not answer:
        return False

    key = f"captcha:{captcha_id}"
    stored_answer = cache.get(key)

    if stored_answer is None:
        # 验证码不存在或已过期
        return False

    # 不区分大小写比较
    if stored_answer.upper() == answer.upper():
        # 验证成功后删除验证码（防止重复使用）
        cache.delete(key)
        return True

    return False


def find_user_by_email_or_username(email_or_username):
    """
    通过邮箱或用户名查找用户

    Args:
        email_or_username: 邮箱地址或用户名

    Returns:
        User实例或None: 找到的用户，如果不存在则返回None
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if "@" in email_or_username:
        # 通过邮箱查找
        try:
            return User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            return None
    else:
        # 通过用户名查找
        try:
            return User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            return None
