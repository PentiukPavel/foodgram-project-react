from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизированная модель пользователей."""

    USER = 'user'

    ROLE_CHOISES = (
        (USER, 'пользователь'),
    )

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
        blank=True,
    )

    role = models.CharField(
        'Роль пользователя',
        max_length=13,
        choices=ROLE_CHOISES,
        default=USER,
        blank=False,
        null=False,
    )

    @property
    def is_user(self):
        return self.role == User.USER
