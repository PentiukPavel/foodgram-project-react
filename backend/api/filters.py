from django_filters import (BooleanFilter, CharFilter, FilterSet,
                            ModelMultipleChoiceFilter)

from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтры для рецептов."""

    author = CharFilter(field_name='author__email', lookup_expr='exact')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all(),)
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по наличию в избранном."""

        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorited=user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по наличию в списке покупок."""

        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_shopping_cart=user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name', ]
