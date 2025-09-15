# -*- coding: utf-8 -*-
"""Feature Flags模型"""

from django.db import models


class FeatureFlag(models.Model):
    """功能开关模型"""

    name = models.CharField(max_length=100, unique=True, verbose_name="功能名称")
    description = models.TextField(blank=True, verbose_name="功能描述")
    is_enabled = models.BooleanField(default=False, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "功能开关"
        verbose_name_plural = "功能开关"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({'启用' if self.is_enabled else '禁用'})"
