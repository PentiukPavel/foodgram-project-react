from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.models import Ingredients, Recipes, Tag
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, TagSerializer,)

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

    queryset = Recipes.objects.all()
    pagination_class = LimitOffsetPagination
    filterset_class = RecipeFilter
    filterset_fields = ('author', 'tags', 'favorited', 'in_shopping_cart',)

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""

        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
        return RecipeCreateSerializer
