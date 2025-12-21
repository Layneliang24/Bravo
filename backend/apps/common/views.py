"""通用视图模块"""

from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """健康检查API视图"""

    permission_classes = [AllowAny]  # 允许匿名访问

    @extend_schema(
        summary="健康检查",
        description="检查API服务运行状态",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "message": {"type": "string", "example": "Bravo API is running"},
                    "version": {"type": "string", "example": "1.0.0"},
                    "timestamp": {"type": "string", "example": "2024-01-15T10:00:00Z"},
                },
            }
        },
        tags=["通用"],
    )
    def get(self, request):
        """健康检查端点"""
        data = {
            "status": "healthy",
            "message": "Bravo API is running",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat() + "Z",
        }

        response = Response(data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def post(self, request):
        """健康检查端点（POST方法支持）"""
        return self.get(request)

    def options(self, request):
        """处理预检请求"""
        response = Response({}, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


# 保持向后兼容的函数视图（用于urls_test.py中的common/路径）
def health_check(request):
    """健康检查端点（函数视图，保持向后兼容）"""
    view = HealthCheckView.as_view()
    return view(request)


class ApiInfoView(APIView):
    """API信息API视图"""

    permission_classes = [AllowAny]  # 允许匿名访问

    @extend_schema(
        summary="API信息",
        description="返回API服务基本信息",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Bravo API"},
                    "version": {"type": "string", "example": "1.0.0"},
                    "description": {
                        "type": "string",
                        "example": "Bravo项目后端API服务",
                    },
                    "endpoints": {
                        "type": "object",
                        "properties": {
                            "health": {"type": "string", "example": "/health/"},
                            "api_info": {"type": "string", "example": "/api/info/"},
                            "blog": {"type": "string", "example": "/api/v1/blog/"},
                            "users": {"type": "string", "example": "/api/v1/auth/"},
                        },
                    },
                },
            }
        },
        tags=["通用"],
    )
    def get(self, request):
        """API信息端点"""
        data = {
            "name": "Bravo API",
            "version": "1.0.0",
            "description": "Bravo项目后端API服务",
            "endpoints": {
                "health": "/health/",
                "api_info": "/api/info/",
                "blog": "/api/v1/blog/",
                "users": "/api/v1/auth/",
            },
        }

        response = Response(data, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def post(self, request):
        """API信息端点（POST方法支持）"""
        return self.get(request)

    def options(self, request):
        """处理预检请求"""
        response = Response({}, status=status.HTTP_200_OK)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


# 保持向后兼容的函数视图（用于urls_test.py中的common/路径）
def api_info(request):
    """API信息端点（函数视图，保持向后兼容）"""
    view = ApiInfoView.as_view()
    return view(request)
