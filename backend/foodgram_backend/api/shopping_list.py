from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient


def get_ingredients_for_shopping(user):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shoppingcarts__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit',
    ).annotate(
        value=Sum('amount')
    ).order_by('ingredient__name')
    response = HttpResponse(
        content_type='text/plain',
        charset='utf-8',
    )
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    response.write('Список продуктов к покупке:\n')
    for ingredient in ingredients:
        response.write(
            f'- {ingredient["ingredient__name"]} '
            f'- {ingredient["value"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    return response
