from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from users.models import User
from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    """Класс для поиска ингредиентов по названию."""
    search_param = 'name'


class RecipeFilter(FilterSet):
    """Класс-фильтр выдачи по рецептам."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Метод фильтрации по избранным рецептам."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод фильтрации по рецептам из корзины покупок."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
