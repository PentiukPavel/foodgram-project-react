from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination


class UserViewSet(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    pagination_class = LimitOffsetPagination
