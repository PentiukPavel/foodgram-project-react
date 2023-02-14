from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизированная модель пользователей."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        blank=False,
        null=False,
        unique=True,
        )

    subscriptions = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        verbose_name='Подписки',
    )
