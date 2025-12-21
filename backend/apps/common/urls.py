"""通用URL配置"""

from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health_check"),
    path("info/", views.ApiInfoView.as_view(), name="api_info"),
]
