from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    TYPES = (
        ('card_created', 'Создание карточки'),
        ('card_updated', 'Обновление карточки'),
        ('moderation_request', 'Запрос на модерацию'),
        ('moderation_approved', 'Одобрение модерации'),
        ('moderation_rejected', 'Отказ в модерации'),
    )

    entity_id = models.PositiveIntegerField(verbose_name='ID связанной сущности')
    type = models.CharField(max_length=32, choices=TYPES, verbose_name='Тип уведомления')
    recipient = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='notifications', verbose_name='Получатель'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    data = models.JSONField(verbose_name='Дополнительные данные')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f'Уведомление #{self.id} для {self.recipient}'
