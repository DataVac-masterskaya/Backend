from typing import Any

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models

ACTION_CHOICES = {
    'login': 'Успешный вход',
    'login_failed': 'Неудачная попытка входа',
    'user_create': 'Создание нового редактора',
    'role_change': 'Изменение роли пользователя',
    'block': 'Блокировка/разблокировка учетной записи',
    'card_create': 'Создание новой карточки',
    'card_update': 'Сохранение изменений в черновик',
    'card_submit': 'Отправка версии на модерацию',
    'card_hide': 'Скрытие карточки',
    'card_publish': 'Ручная публикация',
    'card_delete': 'Архивация карточки',
    'moderation_approve': 'Одобрение версии администратором',
    'moderation_reject': 'Отклонение версии с комментарием',
}


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='user_id',
        related_name='audit_logs',
    )
    entity_type = models.CharField(max_length=100)
    entity_id = models.BigIntegerField(null=True, blank=True)
    action_type = models.CharField(max_length=100, choices=ACTION_CHOICES)
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ('-created_at',)
        verbose_name = 'Запись журнала аудита'
        verbose_name_plural = 'Записи журнала аудита'

    def __str__(self) -> str:
        return self.action_type[:30]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            raise PermissionDenied('Нельзя изменять записи журнала аудита.')
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        raise PermissionDenied('Нельзя удалять записи журнала аудита.')
