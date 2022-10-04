from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    """Класс админки для модели пользователя."""
    model = models.User
    list_display = (
       'username',
       'email',
       'first_name',
       'last_name',
       'is_staff',
    )
    list_filter = ('email', 'username',)
    search_fields = ('username', 'email', 'first_name', 'last_name', )
    empty_value_display = '-пусто-'


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Класс админки для модели подписок."""
    model = models.Subscription
    list_display = ('author', 'user', )
    list_filter = ('author', 'user', )
    search_fields = ('author', 'user', )
