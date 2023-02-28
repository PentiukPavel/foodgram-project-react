from django_filters import (CharFilter, FilterSet, ModelChoiceFilter,
                            ModelMultipleChoiceFilter)

from foodgram.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтры для рецептов."""

    author = CharFilter(field_name='author__username', lookup_expr='exact')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all(),)
    is_favorited = ModelChoiceFilter(to_field_name='favorited',
                                     method='filter_is_favorited')
    is_in_shopping_cart = ModelChoiceFilter(to_field_name='in_shopping_cart',
                                            method='filter_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по наличию в избранном."""

        if value:
            user = self.request.user
            return queryset.filter(favorited=user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по наличию в списке покупок."""

        if value:
            user = self.request.user
            return queryset.filter(in_shopping_cart=user)
        return queryset
