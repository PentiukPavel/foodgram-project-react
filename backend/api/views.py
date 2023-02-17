from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.models import Ingredients, Recipes, Tag
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, SubscribeGetSerializer,
                          SubscribePostDeleteSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_field = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    pagination_class = LimitOffsetPagination
    filterset_class = RecipeFilter
    filterset_fields = ('author', 'tags', 'favorited', 'in_shopping_cart',)

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""

        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        return Recipes.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomUserView(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=[
            'post',
            'delete',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribePostDeleteSerializer,
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        author = User.objects.get(id=self.serializer.data['id'])
        user = self.request.user
        if request.method == 'POST':
            user.subscriptions.add(author)
        if request.method == 'DELETE':
            user.subscriptions.remove(author)

    @action(
        detail=False,
        methods=[
            'list',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribeGetSerializer,
        url_path='subscriptions',
    )
    def subscriptions(self, request, **kwargs):
        return Response(self.serializer.data)
