from django.shortcuts import get_object_or_404
from foodgram.models import Recipe
from rest_framework.response import Response

from .serializers import RecipeForSubscriptionsSerializer


def add_to_field(self, request, field_name, message, **kwargs):
    """
    Метод для добавления и удаления значений в ManyToManyField модели Recipe.
    """

    recipe = get_object_or_404(Recipe, id=kwargs['pk'])
    user = self.request.user
    field_value = getattr(recipe, field_name)
    if request.method == 'POST':
        if field_value.filter(pk=user.id).exists():
            return Response({'errors': f'Рецепт уже в { message }.'})
        field_value.add(user)
    if request.method == 'DELETE':
        if field_value.filter(pk=user.id).exists():
            field_value.remove(user)
        else:
            return Response({'errors': f'Рецепта нет в { message }.'})
    return RecipeForSubscriptionsSerializer(recipe)
