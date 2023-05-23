from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
)


class User(AbstractUser):
    """
    Модель пользователя платформы.
    Используется в системе аутентификации Django.
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        max_length=250,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        max_length=100,
        blank=True
    )
    last_name = models.CharField(
        max_length=100,
        blank=True
    )
    bio = models.TextField(
        blank=True
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='user'
    )

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
