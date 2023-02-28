from django_filters import BooleanFilter, CharFilter, FilterSet

from foodgram.models import Recipe


class RecipeFilter(FilterSet):
    """Фильтры для рецептов."""

    author = CharFilter(field_name='author__username', lookup_expr='exact')
    tags = CharFilter(field_name='tags__slug', lookup_expr='exact')
    is_favorited = BooleanFilter(field_name='favorited')
    is_in_shopping_cart = BooleanFilter(field_name='in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'favorited', 'in_shopping_cart', ]
