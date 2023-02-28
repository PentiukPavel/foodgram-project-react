from rest_framework.pagination import PageNumberPagination


class SubscriptionPaginator(PageNumberPagination):
    """Кастомный пагинатор для подписок."""

    page_size_query_param = 'limit'
