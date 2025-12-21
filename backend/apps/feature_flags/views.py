# -*- coding: utf-8 -*-
"""Feature Flags视图"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class FeatureFlagsStatusView(APIView):
    """功能开关状态API视图"""

    permission_classes = []  # 允许匿名访问

    @extend_schema(
        summary="获取功能开关状态",
        description="返回功能开关模块状态",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "message": {
                        "type": "string",
                        "example": "Feature flags module loaded",
                    },
                },
            }
        },
        tags=["功能开关"],
    )
    def get(self, request):
        """返回功能开关状态"""
        return Response(
            {"status": "ok", "message": "Feature flags module loaded"},
            status=status.HTTP_200_OK,
        )
