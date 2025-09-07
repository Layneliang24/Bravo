"""
Bravo 项目 URL 配置模板

`urlpatterns` 列表将 URL 路由到视图。有关更多信息，请参阅：
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
示例：
函数视图
    1. 添加导入：from my_app import views
    2. 添加 URL 到 urlpatterns：path('', views.home, name='home')
基于类的视图
    1. 添加导入：from other_app.views import Home
    2. 添加 URL 到 urlpatterns：path('', Home.as_view(), name='home')
包含另一个 URLconf
    1. 导入 include() 函数：from django.urls import include, path
    2. 添加 URL 到 urlpatterns：path('blog/', include('blog.urls'))
"""
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import include, path


def home_view(request):
    """根路径视图，返回API信息"""
    return JsonResponse(
        {
            "message": "Welcome to Bravo API",
            "version": "1.0.0",
            "endpoints": {
                "api_docs": "/api/docs/",
                "admin": "/admin/",
                "health": "/health/",
                "api": {
                    "auth": "/api/v1/auth/",
                    "blog": "/api/v1/blog/",
                    "english": "/api/v1/english/",
                    "jobs": "/api/v1/jobs/",
                },
            },
        }
    )


urlpatterns = [
    # 根路径
    path("", home_view, name="home"),
    # 管理后台
    path("admin/", admin.site.urls),
    # API 文档
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # API 路由
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/blog/", include("apps.blog.urls")),
    path("api/v1/english/", include("apps.english.urls")),
    path("api/v1/jobs/", include("apps.jobs.urls")),
    # 健康检查
    path("health/", include("health_check.urls")),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # 调试工具栏
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
