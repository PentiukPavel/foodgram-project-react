from foodgram.models import RecipeIngredient, RecipeTag


def tags_and_ingredients_create(tags, ingredients, recipe):
    """
    Метод для создания тегов и ингредиентов рецепта.
    """

    RecipeTag.objects.bulk_create(
        [RecipeTag(tag=tag, recipe=recipe) for tag in tags]
    )
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(ingredient=ingredient['id'],
                          recipe=recipe,
                          amount=ingredient['amount'])
            for ingredient in ingredients]
    )
