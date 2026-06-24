from django.conf import settings
from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'Активен'
    BLOCKED = 'blocked', 'Заблокирован'
    DELETED = 'deleted', 'Удалён'


class Role(models.Model):
    name=models.CharField(
        verbose_name='Название роли',
        max_length=32
    )

    def __str__(self):
        return f'{self.id} - {self.name}'

    class Meta:
        verbose_name = 'роль'
        verbose_name_plural = 'роли'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    role_id = models.ForeignKey(
        'Role',
        verbose_name='ID роли',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    full_name = models.CharField(
        verbose_name='ФИО',
        max_length=255,
    )

    status = models.CharField(
        max_length=50,
        verbose_name='Статус',
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE
    )

    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Создан пользователем',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    class Meta:
        verbose_name = 'дополнительные данные пользователя'
        verbose_name_plural = 'дополнительные данные пользователей'

    def __str__(self):
            return f'{self.user.username}'
