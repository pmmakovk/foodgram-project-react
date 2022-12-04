from django.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator
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

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


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


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели связи ингредиентов и рецептов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit', )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    image = Base64ImageField()
    ingredients = IngredientRecipeGetSerializer(
        many=True,
        read_only=True,
        source='recipeingredients'
    )
    tags = TagSerializer(many=True)
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


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Класс-сериализатор модели рецепт для создания и изменения."""
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientAmountSerializer(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, ingredients):
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1!'
                )
        chek_id = [ingredient['id'] for ingredient in ingredients]
        if len(chek_id) != len(set(chek_id)):
            raise serializers.ValidationError(
                'Данный ингредиент уже есть в рецепте!')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо выбрать теги!')
        return tags

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        """
        Вспомогательный метод создания объектов
        связанной модели ингредиенты рецепта.
        """
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            ingredient_id=ingredient.get('id'),
            amount=ingredient.get('amount'),
            recipe=recipe
        ) for ingredient in ingredients])
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(
            tags, ingredients, recipe
        )

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        return self.add_ingredients_and_tags(
            tags, ingredients, instance
        )

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data
