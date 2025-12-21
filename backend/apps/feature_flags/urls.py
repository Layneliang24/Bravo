# -*- coding: utf-8 -*-
"""Feature Flags URL配置"""

from django.urls import path

from . import views

app_name = "feature_flags"  # pylint: disable=invalid-name

urlpatterns = [
    path("status/", views.FeatureFlagsStatusView.as_view(), name="status"),
]
