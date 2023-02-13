from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
