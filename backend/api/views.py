from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.models import Ingredient, Recipe, Tag
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import AdminAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeGetSerializer,
                          SubscribeGetSerializer, TagSerializer)
from .utils import add_to_field

User = get_user_model()


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_field = ('^name',)


class RecipeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Вьюсет для рецептов."""

    permission_classes = (AdminAuthorOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filterset_class = RecipeFilter
    filterset_fields = ('author', 'tags', 'favorited', 'in_shopping_cart',)
    serializer_class = RecipeGetSerializer

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""

        if self.action in ['list', 'retrieve', ]:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=[
            'post',
            'delete',
        ],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, **kwargs):
        """
        Добавление рецепта в избранное
        и удаление из него.
        """

        response = add_to_field(self,
                                request,
                                field_name='favorited',
                                message='избранном',
                                **kwargs)
        return Response(response.data)

    @action(
        detail=True,
        methods=[
            'post',
            'delete',
        ],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
    )
    def in_shopping_cart(self, request, **kwargs):
        """
        Добавление рецепта в список покупок
        и удаление из него.
        """

        response = add_to_field(self,
                                request,
                                field_name='in_shopping_cart',
                                message='списке покупок',
                                **kwargs)
        return Response(response.data)

    @action(
        detail=False,
        methods=[
            'get',
        ],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Загрузка списка покупок."""

        user = self.request.user
        recipes = user.shopping_cart.all()
        ingredients = {}
        line_break = '\n'
        for recipe in recipes:
            recipe_ingredients = recipe.ingredients.all()
            for ingredient in recipe_ingredients:
                amount = ingredient.recipeingredient_set.get(
                    ingredient=ingredient,
                    recipe=recipe
                ).amount
                key = f'{ ingredient.name } ({ ingredient.measurement_unit })'
                ingredients[key] = ingredients.get(key, 0) + amount
        result = []
        for ingredient, amount in ingredients.items():
            result.append(f'{ingredient} - {amount} {line_break}')

        return HttpResponse(result, headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': 'attachment; filename="cart.txt"',
        })


class CustomUserView(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=[
            'post',
            'delete',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribeGetSerializer,
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        """Подписка на пользователя и отписка от него."""

        author = User.objects.get(id=kwargs['id'])
        user = self.request.user
        if request.method == 'POST':
            if author == user:
                return Response({'errors': 'Нельзя подписаться на себя.'})
            if user.subscriptions.filter(pk=author.id).exists():
                return Response({'errors': 'Вы уже подписаны на автора.'})
            user.subscriptions.add(author)
        if request.method == 'DELETE':
            if user.subscriptions.filter(pk=author.id).exists():
                user.subscriptions.remove(author)
            else:
                return Response({'errors': 'Вы не подписаны на автора.'})
        serializer = self.get_serializer(author)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=[
            'get',
        ],
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscribeGetSerializer,
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Вывести список подписок."""
        user = self.request.user
        subscriptions = user.subscriptions
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
