from django_filters import BooleanFilter, CharFilter, FilterSet

from foodgram.models import Recipe


class RecipeFilter(FilterSet):
    """Фильтры для рецептов."""

    author = CharFilter(field_name='author__username', lookup_expr='exact')
    tags = CharFilter(field_name='tags__slug', lookup_expr='exact')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(field_name='in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        return queryset.filter(pk=user.id)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'favorited', 'in_shopping_cart', ]
