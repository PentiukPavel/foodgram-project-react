from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (UserSerializer, SubscribeGetSerializer,
                          SubscribePostDeleteSerializer)

User = get_user_model()


class CustomUserView(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    @action(
        methods=[
            'post',
            'delete',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribePostDeleteSerializer,
        url_path='subscribe/',
    )
    def subscribe(self, request, **kwargs):
        author = User.objects.get(id=self.serializer.data['id'])
        user = self.request.user
        if request.method == 'POST':
            user.subscriptions.add(author)
        if request.method == 'DELETE':
            user.subscriptions.remove(author)

    @action(
        methods=[
            'list',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribeGetSerializer,
        url_path='subscriptions/',
    )
    def subscriptions(self, request, **kwargs):
        return Response(self.serializer.data)
