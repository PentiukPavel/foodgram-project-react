from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        'Название',
        max_length=200,
        blank=False,
        null=False,
        help_text='Название тега',
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        blank=False,
        null=True,
        help_text='Цвет тега в HEX',
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        blank=False,
        null=False,
        help_text='Уникальный слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredients(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        'Название',
        max_length=200,
        blank=False,
        null=False,
        help_text='Название ингредиента',
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False,
        null=False,
        help_text='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель для рецептов."""

    name = models.CharField(
        'Название',
        max_length=200,
        blank=False,
        null=False,
        help_text='Название рецепта',
    )
    text = models.TextField(
        'Описание',
        blank=False,
        null=False,
        help_text='Описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        help_text='Список тегов',
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient',
        help_text='Список ингредиентов',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        help_text='Время приготовления (в минутах)',
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                1,
                'Время приготовления не может быть мнеьше 1 минуты.'
            )
        ]
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipes/images/',
        help_text='Ссылка на картинку на сайте',
        blank=False,
        null=False,
    )
    favorited = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='В избранном',
    )
    in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='В листе покупок',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Модель для связи рецептов и тегов."""

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    """Модель для связи рецептов и ингредиентов."""

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'Количество',
        help_text='Количество в единицах измерения',
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингрединент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
