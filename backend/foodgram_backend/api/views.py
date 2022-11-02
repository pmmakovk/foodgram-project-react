from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers, filters, shopping_list
from .permissions import IsAuthorOrReadOnly
from users.models import User
from recipes.models import (
    Tag, Ingredient,  Recipe, Favorite, ShoppingCart, RecipeIngredient)
from api.pagination import PageLimitPagination


class UserViewSet(UserViewSet):
    """Класс-контроллер для модели пользователя."""
    pagination_class = PageLimitPagination

    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        """Метод эндпоинта с информацией о текущем пользователе."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated, ))
    def subscribe(self, request, *args, **kwargs):
        """Метод эндпоинта подписки/отписки на автора."""
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            data = request.data.copy()
            data.update({'author': author.id})
            serializer = serializers.SubscriptionSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=self.get_serializer(author).data)
        obj = request.user.subscriber.filter(author=author)
        if not obj.exists():
            return Response(
                {'errors': 'Вы не подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'], detail=False,
        permission_classes=(permissions.IsAuthenticated, ),
        serializer_class=serializers.SubscriptionInfoSerializer)
    def subscriptions(self, request, *args, **kwargs):
        """Метод эндпоинта подписок текущего пользователя."""
        queryset = request.user.subscriber.all()
        pages = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс-контроллер модели тег."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс-контроллер модели ингредиент."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.IngredientSearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс-контроллер модели рецепт."""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    filter_class = filters.RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RecipeSerializer
        return serializers.RecipePostSerializer

    def create_del_obj(self, request, pk, database):
        """Вспомогательный метод создания объекта избранного/списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                database.objects.create(
                    user=self.request.user,
                    recipe=recipe)
                serializer = serializers.PartialRecipeSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'errors: Объект уже в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).exists():
                database.objects.filter(
                    user=self.request.user,
                    recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'errors: Объект не в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)
        else:
            text = 'errors: Метод обращения недопустим.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated, ))
    def favorite(self, request, pk=None):
        """Метод эндпоинта добавления/удаления рецепта из списка избранного."""
        return self.create_del_obj(request, pk, Favorite)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated, ),)
    def shopping_cart(self, request, pk):
        """Метод эндпоинта добавления/удаления рецепта из списка покупок."""
        return self.create_del_obj(request, pk, ShoppingCart)

    @action(
        methods=['get'], detail=False,
        permission_classes=(permissions.IsAuthenticated, ))
    def download_shopping_cart(self, request):
        """Метод эндпоинта скачивания списка покупок PDF файлом."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit')
        cart = {}
        for name, amount, unit in ingredients:
            if name not in cart:
                cart[name] = {'amount': amount, 'unit': unit}
            else:
                cart[name]['amount'] += amount
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"')
        return shopping_list.pfd_table(response, cart)
