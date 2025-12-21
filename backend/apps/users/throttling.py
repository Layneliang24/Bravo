# -*- coding: utf-8 -*-
# REQ-ID: REQ-2025-003-user-login
"""用户认证相关的频率限制"""

from rest_framework.throttling import SimpleRateThrottle


class PreviewLoginThrottle(SimpleRateThrottle):
    """登录预验证API频率限制

    限制同一IP每分钟最多10次请求

    重要：OPTIONS预检请求不计入限流，避免CORS预检触发限流
    """

    scope = "preview_login"
    rate = "10/min"

    def allow_request(self, request, view):
        """
        判断是否允许请求

        重要：OPTIONS预检请求（CORS）不计入限流
        这样可以避免浏览器的CORS预检请求触发频率限制
        """
        # OPTIONS请求是CORS预检请求，不计入限流
        if request.method == "OPTIONS":
            return True

        # 其他请求正常进行限流检查
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        """
        获取缓存键，基于IP地址

        Args:
            request: HTTP请求对象
            view: 视图对象

        Returns:
            str: 缓存键，格式为 'throttle_preview_login_{ip}'
        """
        if request.user.is_authenticated:
            # 如果用户已登录，使用用户ID作为键
            ident = request.user.id
        else:
            # 如果用户未登录，使用IP地址作为键
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
