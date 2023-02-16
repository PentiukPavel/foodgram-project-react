from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from api.serializers import RecipeForSubscriptionsSerializer

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


class SubscribePostDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и удалений подписки."""

    class Meta:
        model = User
        fields = ('subscriptions',)

    def to_representation(self, instance):
        """Вид данных сериализатора."""
        representation = super().to_representation(instance)
        subscriptions = representation['subscriptions']
        return {
            'id': subscriptions
        }

    def id_validate(self, value):
        """Проверка на подписку на самого себя."""
        if self.context['request'].user == value['id']:
            raise serializers.ValidationError(
                'Нельзя пописываться на самого себя.'
            )
        return value


class SubscribeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeForSubscriptionsSerializer(many=True,
                                               read_only=True,
                                               source='user.recipes',)

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
        return self.context.get('request').user in obj.followers.all()

    def get_recipes_count(self, obj):
        return self.recipes.count()
