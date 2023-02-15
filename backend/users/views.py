from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination

from .serializers import UserSerializer

User = get_user_model()


class CustomUserView(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer
