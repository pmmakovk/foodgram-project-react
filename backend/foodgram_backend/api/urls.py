from django.urls import path, include
from djoser.urls.authtoken import urlpatterns
from rest_framework.routers import DefaultRouter

from . import views


router_v1 = DefaultRouter()
router_v1.register(r'users', views.UserViewSet, basename='user')
router_v1.register(
    r'ingredients', views.IngredientViewSet, basename='ingredient')
router_v1.register(r'recipes', views.RecipeViewSet, basename='recipe')
router_v1.register(r'tags', views.TagViewSet, basename='tag')


urlpatterns = [
    path('auth/', include(urlpatterns)),
    path('', include(router_v1.urls)),
]
