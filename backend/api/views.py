from django_filters.rest_framework import DjangoFilterBackend
from foodgram.models import Ingredients, Tag
from rest_framework import filters, mixins, viewsets

from .serializers import IngredientSerializer, TagSerializer


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
