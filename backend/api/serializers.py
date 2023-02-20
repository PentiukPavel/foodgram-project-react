from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers

from .fields import Base64ImageField
from .serializers_utils import tags_and_ingredients_create

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        """Отметка о подписке на автора."""

        user = self.context.get('request').user
        return obj.followers.filter(subscriptions=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сeриализатор для создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',)

    def validate_ingredients(self, value):
        """Проверка уникальности ингредиентов."""

        result = []
        for ingredient in value:
            if ingredient in result:
                ing_name = ingredient['id']
                raise serializers.ValidationError(
                    f'В списке ингредиентов есть повторяющиеся: { ing_name }.'
                )
            result.append(ingredient)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        tags_and_ingredients_create(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        tags_and_ingredients_create(tags, ingredients, instance)
        return super().update(instance, validated_data)


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def get_is_in_shopping_cart(self, obj):
        """Рецепт в списке покупок у пользователя."""

        user = self.context.get('request').user
        return Recipe.objects.filter(id=obj.id, in_shopping_cart=user).exists()

    def get_is_favorited(self, obj):
        """Рецепт в избраном у пользователя."""

        user = self.context.get('request').user
        return Recipe.objects.filter(id=obj.id, favorited=user).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredients = representation['ingredients']
        for ingredient in ingredients:
            amount = RecipeIngredient.objects.get(ingredient=ingredient['id'],
                                                  recipe=instance).amount
            ingredient['amount'] = amount
        return representation


class RecipeForSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в подписках."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)


class SubscribeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeForSubscriptionsSerializer(many=True,
                                               read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """Отметка о подписке на автора."""

        user = self.context.get('request').user
        return obj.followers.filter(subscriptions=user).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора."""

        recipes = obj.recipes.all()
        return RecipeForSubscriptionsSerializer(recipes, many=True)

    def get_recipes_count(self, obj):
        """Подсчет количества рецептов автора."""

        user = get_object_or_404(
            User,
            id=obj.id)
        return user.recipes.count()
