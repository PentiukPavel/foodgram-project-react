from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизированная модель пользователей."""
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        blank=False,
        null=False,
        )

    subscriptions = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        verbose_name='Подписки',
    )

    def get_is_subscribed(self, obj):
        return self.context['user'] in obj.followers.all()
