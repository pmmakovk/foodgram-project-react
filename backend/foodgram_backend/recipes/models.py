from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель для тегов."""
    name = models.CharField('Название', max_length=255, unique=True)
    color = ColorField(default='#49B64E', verbose_name='Цвет', unique=True)
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField(
        default='г',
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Длительность приготовления', validators=[MinValueValidator(1)])
    image = models.ImageField('Картинка', upload_to='recipe', blank=True, )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги')

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_ingredients(self):
        return '\n'.join([ing.name for ing in self.ingredients.all()])

    def get_tags(self):
        return '\n'.join([tag.name for tag in self.tags.all()])

    get_ingredients.short_description = 'Ингредиенты'
    get_tags.short_description = 'Теги'


class RecipeIngredient(models.Model):
    """Класс модели связи между рецептами и ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipeingredients',
        on_delete=models.SET_NULL,
        null=True
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipeingredients',
        on_delete=models.SET_NULL,
        null=True
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(1)])

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe', ),
                name='unique_ingredients_recipe')
        ]

    def __str__(self):
        return f'{self.ingredient} входит в состав {self.recipe}.'


class BaseFavorite(models.Model):
    """Базовый класс избранных рецептов."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='%(class)ss', verbose_name='Рецепт')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='%(class)ss', verbose_name='Пользователь')

    class Meta:
        abstract = True
        ordering = ('-id', )


class Favorite(BaseFavorite):
    """Класс модели избранных рецептов."""

    class Meta(BaseFavorite.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe', ), name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}.'


class ShoppingCart(BaseFavorite):
    """Класс модели списка покупок."""

    class Meta(BaseFavorite.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe', ), name='unique_cart')
        ]

    def __str__(self):
        return f'{self.recipe} в корзине покупок у {self.user}.'
