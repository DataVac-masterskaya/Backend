from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.constants import FULL_NAME_MAX_LENGTH, ROLE_MAX_LENGTH


class RoleChoices(models.TextChoices):
    """Роли пользователей."""

    ADMIN = 'admin', 'администратор'
    MODERATOR = 'moderator', 'модератор'


class User(AbstractUser):
    """Базовая модель пользователя наследуется от AbstractUser."""

    full_name = models.CharField(max_length=FULL_NAME_MAX_LENGTH, verbose_name='Полное Имя')
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH, choices=RoleChoices.choices, default=RoleChoices.MODERATOR, verbose_name='Роль'
    )
    email = models.EmailField(unique=True, verbose_name='Емаил')

    @property
    def is_admin(self):
        """Проверяет является ли пользователь администратором."""
        return self.role == RoleChoices.ADMIN

    @property
    def is_moderator(self):
        """Проверяет является пользователь модератором."""
        return self.role == RoleChoices.MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('full_name',)

    def __str__(self):
        return self.full_name
