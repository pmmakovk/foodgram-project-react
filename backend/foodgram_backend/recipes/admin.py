from django.contrib import admin

from recipes import models


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    min_num = 1
    extra = 0


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс админки для модели рецептов."""
    model = models.Recipe
    list_display = (
        'name', 'author', 'cooking_time', 'get_ingredients', 'get_tags', )
    list_filter = ('author', 'tags', )
    search_fields = (
        'name', 'author', 'get_ingredients', 'get_tags', )
    inlines = (RecipeIngredientInline, )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс админки для модели тегов."""
    model = models.Tag
    list_display = ('name', 'slug', 'color', )
    list_filter = ('name', 'slug', )
    search_fields = ('name', 'slug', )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс админки для модели пользователя."""
    model = models.Ingredient
    list_display = ('name', 'measurement_unit', )
    list_filter = ('measurement_unit', )
    search_fields = ('name', 'measurement_unit', )


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Класс админки для модели связи ингредиентов и рецептов."""
    model = models.RecipeIngredient
    list_display = ('recipe', 'ingredient', )
    list_filter = ('recipe', 'ingredient', )
    search_fields = ('recipe', 'ingredient', )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс админки для модели избранного."""
    model = models.Favorite
    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс админки для модели избранного."""
    model = models.ShoppingCart
    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )
