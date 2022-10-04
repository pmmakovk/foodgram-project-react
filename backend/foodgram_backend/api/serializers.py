from django.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Subscription
from recipes.models import (
    Tag, Ingredient, RecipeIngredient, Recipe, Favorite, ShoppingCart)


class BaseFavoriteSerializer(serializers.ModelSerializer):
    """Базовый класс-сериализатор списка избранного."""
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())


class FavoriteSerializer(BaseFavoriteSerializer):
    """Класс-сериализатор модели списка избранного."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('recipe', 'user', ))]

    def create(self, validated_data):
        return Favorite.objects.create(
            user=self.context.get('request').user, **validated_data)


class ShoppingCartSerializer(BaseFavoriteSerializer):
    """Класс-сериализатор модели корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('recipe', 'user', ))]

    def create(self, validated_data):
        return ShoppingCart.objects.create(
            user=self.context.get('request').user, **validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор класса подписок."""
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('author', 'user', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'user', )
            )
        ]

    def create(self, validated_data):
        return Subscription.objects.create(
            user=self.context.get('request').user, **validated_data
        )

    def validate_author(self, value):
        """Метод валидации поля автор."""
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        return value


class PartialRecipeSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели рецептов для получения части данных о них."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )
        read_only_fields = ('id', 'name', 'image', 'cooking_time', )


class SubscriptionInfoSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели подписок для вывода информации о подписке."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """Метод проверки подписки пользователя на автора."""
        return Subscription.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        """Метод вывода рецептов автора."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit', settings.PAGE_SIZE)
        queryset = obj.author.recipes.all()[:int(recipes_limit)]
        return PartialRecipeSerializer(
            queryset, many=True).data

    def get_recipes_count(self, obj):
        """Метод вывода количества рецептов автора."""
        return obj.author.recipes.count()


class UserInfoSerializer(UserSerializer):
    """Сериализатор класса пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = ('email', )

    def get_is_subscribed(self, obj):
        """Метод проверки подписки пользователя на автора."""
        user = self.context.get('request').user
        return user.is_authenticated and Subscription.objects.filter(
            user=user, author=obj.id).exists()


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор класса пользователей для регистрации."""
    email = serializers.EmailField(
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta(UserCreateSerializer.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'password', )


class TagSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели тег."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели ингредиент."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели связи ингредиентов и рецептов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit', )
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=('ingredient', 'recipe', ))]


class RecipeSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели рецепт для создания и изменения."""
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredients', many=True, read_only=True)
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    def get_author(self, obj):
        """Метод получения информации об авторе рецепта."""
        return UserInfoSerializer(
            obj.author, read_only=True,
            context={'request': self.context.get('request')}).data

    def get_is_favorited(self, obj):
        """Метод получения информации о том, является ли рецепт избранным."""
        user = self.context.get('request').user
        return user.is_authenticated and (
            user.favorites.filter(recipe__id=obj.id).exists())

    def get_is_in_shopping_cart(self, obj):
        """Метод получения информации о том, находится ли рецепт в корзине."""
        user = self.context.get('request').user
        return user.is_authenticated and (
            user.shoppingcarts.filter(recipe__id=obj.id).exists())

    def create_ingredients(self, ingredients, recipe):
        """
        Вспомогательный метод создания объектов
        связанной модели ингредиенты рецепта.
        """
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe, ingredient_id=ingredient.get('id'),
            amount=ingredient.get('amount')) for ingredient in ingredients])

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(self.initial_data.get('tags'))
        self.create_ingredients(self.initial_data.get('ingredients'), recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.clear()
        instance.tags.set(self.initial_data.get('tags'))
        instance.recipeingredients.all().delete()
        self.create_ingredients(self.initial_data.get('ingredients'), instance)
        instance.save()
        return instance
