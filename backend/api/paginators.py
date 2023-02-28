from rest_framework.pagination import LimitOffsetPagination


class SubscriptionPaginator(LimitOffsetPagination):
    """Кастомный пагинатор для подписок."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
