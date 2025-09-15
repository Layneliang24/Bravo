# -*- coding: utf-8 -*-
"""Feature Flags视图"""

from django.http import JsonResponse


def feature_flags_status(request):  # pylint: disable=unused-argument
    """返回功能开关状态"""
    return JsonResponse({"status": "ok", "message": "Feature flags module loaded"})
