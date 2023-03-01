from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from foodgram.models import Ingredient, Recipe, Tag
from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPaginator
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeGetSerializer,
                          SubscribeGetSerializer, TagSerializer)
from .views_utils import add_to_field

User = get_user_model()


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    permission_classes = (AllowAny, )


class RecipeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Вьюсет для рецептов."""

    permission_classes = (OwnerOrReadOnly, )
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора для рецептов."""

        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        if not self.request.query_params.get('tags'):
            return Recipe.objects.none()
        return Recipe.objects.all().select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

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
        line_break = '\n'
        ings = Ingredient.objects.filter(recipeingredient__recipe__in=recipes)
        ing_values = ings.values(
            'name',
            'measurement_unit').annotate(
                amount=Sum('recipeingredient__amount'))
        result = []
        for value in ing_values:
            name = value['name'].capitalize()
            maesurement_unit = value['measurement_unit']
            amount = value['amount']
            result.append(
                f'{ name } ({ maesurement_unit }) - { amount } { line_break }'
            )
        return HttpResponse(result, headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': 'attachment; filename="cart.txt"',
            }
        )


class CustomUserView(UserViewSet):
    """Вьюсет для пользователей с пагинацией."""

    queryset = User.objects.all()
    pagination_class = CustomPaginator
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


class SubscriptionView(UserViewSet):
    """Вьюсет для подписок пользователя."""

    pagination_class = CustomPaginator
    serializer_class = SubscribeGetSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return user.subscriptions.all()
