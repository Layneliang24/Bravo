"""通用视图模块"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def health_check(request):
    """健康检查端点"""
    if request.method == "OPTIONS":
        # 处理预检请求
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    data = {
        "status": "healthy",
        "message": "Bravo API is running",
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:00:00Z"
    }
    
    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def api_info(request):
    """API信息端点"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    data = {
        "name": "Bravo API",
        "version": "1.0.0",
        "description": "Bravo项目后端API服务",
        "endpoints": {
            "health": "/health/",
            "api_info": "/api/info/",
            "blog": "/api/v1/blog/",
            "users": "/api/v1/auth/",
        }
    }
    
    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    return response
