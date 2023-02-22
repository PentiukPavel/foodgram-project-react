from django.shortcuts import get_object_or_404

from foodgram.models import Ingredient, RecipeIngredient, RecipeTag


def tags_and_ingredients_create(tags, ingredients, recipe):
    """
    Метод для создания тегов и ингредиентов рецепта.
    """

    RecipeTag.objects.bulk_create(
        [RecipeTag(tag=tag, recipe=recipe) for tag in tags]
    )
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(ingredient=get_object_or_404(
                              Ingredient,
                              pk=ing['ingredient']['id']
                         ),
                          recipe=recipe,
                          amount=ing['amount'])
            for ing in ingredients['all']]
    )
