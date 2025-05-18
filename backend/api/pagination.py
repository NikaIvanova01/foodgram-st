from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный класс пагинации с переопределенными параметрами."""
    page_size_query_param = 'limit'
    page_size = 6
