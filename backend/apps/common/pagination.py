# 分页配置模板

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页配置"""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
