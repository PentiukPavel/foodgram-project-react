import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from foodgram.models import Ingredients, RecipeIngredient, Recipes, Tag
from rest_framework import serializers
from users.serializers import CustomUserSerializer

User = get_user_model()


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

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(many=True, read_omly=True)
    ingredients = RecipeIngredientSerializer(many=True, read_omly=True)
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
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, _ = Ingredients.objects.get(
                pk=ingredient['id']
            )
            RecipeIngredient.objects.create(current_ingredient,
                                            recipe=recipe,
                                            amount=ingredients['amount'])
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
        return self.context.get('request').user in obj.in_shopping_cart.all()

    def get_is_favorited(self, obj):
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
