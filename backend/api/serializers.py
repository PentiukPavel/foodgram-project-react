import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.models import (Ingredients, RecipeIngredient, Recipes, RecipeTag,
                             Tag)
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        return self.context.get('request').user in obj.followers.all()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сeриализатор для создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password',)


class Base64ImageField(serializers.ImageField):
    """Сериализатор для фотографий блюд."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
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
        model = Recipes
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        RecipeTag.objects.bulk_create(
            [RecipeTag(tag=tag, recipe=recipe) for tag in tags]
        )
        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient['id'],
                                            recipe=recipe,
                                            amount=ingredient['amount'],)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        for tag in tags:
            RecipeTag.objects.create(tag=tag,
                                     recipe=recipe)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(ingredient=ingredient['id'],
                                            recipe=recipe,
                                            amount=ingredient['amount'],)
        instance.save()
        return recipe


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
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

        return self.context.get('request').user in obj.in_shopping_cart.all()

    def get_is_favorited(self, obj):
        """Рецепт в избраном у пользователя."""

        return self.context.get('request').user in obj.favorited.all()

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
        model = Recipes
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

        return self.context.get('request').user in obj.followers.all()

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
