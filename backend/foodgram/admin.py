from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag

User = get_user_model()


class IngredientsAdmin(admin.ModelAdmin):
    """Модель рецептов для администратора."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientsInLine(admin.StackedInline):
    """Класс для связи рецептов и ингредиентов в админке."""

    model = RecipeIngredient


class TagsInLine(admin.StackedInline):
    """Класс для связи рецептов и тегов в админке."""

    model = RecipeTag


class UserAdmin(admin.ModelAdmin):
    """Модель пользователей для администратора."""

    list_display = ('first_name',
                    'email',
                    'last_name',
                    'username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    """Модель рецептов для администратора."""

    inlines = [IngredientsInLine, TagsInLine, ]
    list_display = ('author',
                    'name',)
    list_filter = ('name', 'tags', 'author',)
    empty_value_display = '-пусто-'
    fields = ('author',
              'name',
              'image',
              'text',
              'cooking_time',
              'favorited',
              'in_shopping_cart',
              'in_favorites')
    readonly_fields = ['in_favorites', ]

    def in_favorites(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorited.count()


admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(RecipeTag)
admin.site.register(Tag)
admin.site.register(User, UserAdmin)
