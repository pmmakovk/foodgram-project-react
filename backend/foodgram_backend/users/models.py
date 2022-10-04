from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Класс модели пользователя."""
    USERNAME_FIELD = 'email'
    email = models.EmailField('Email', max_length=255, unique=True)
    REQUIRED_FIELDS = ('username', )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс модели подписок."""
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('author__id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author', ),
                name='unique_subscription'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]

    DESCRIPTION = '{subscriber} подписан на {subscribing}.'

    def __str__(self):
        return self.DESCRIPTION.format(
            subscriber=self.user.username, subscribing=self.author.username
        )
