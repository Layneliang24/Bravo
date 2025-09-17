# -*- coding: utf-8 -*-
"""Feature Flags应用配置"""

from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    """Feature Flags应用配置类"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.feature_flags"
    verbose_name = "Feature Flags"
