from models.notification import Notification


class NotificationRepository:
    def save(self, notification_data: dict) -> Notification:
        """
        Сохраняет новое уведомление в базе данных
        :param notification_data: Данные уведомления
        :return: Созданный объект уведомления
        """
        return Notification.objects.create(**notification_data)

    def get_by_id(self, notification_id: int) -> Notification:
        """
        Получает уведомление по ID
        :param notification_id: ID уведомления
        :return: Объект уведомления
        """
        return Notification.objects.get(id=notification_id)

    def get_user_notifications(self, user_id: int, limit: int = 10) -> list:
        """
        Получает уведомления для пользователя
        :param user_id: ID пользователя
        :param limit: Лимит уведомлений
        :return: Список уведомлений
        """
        return Notification.objects.filter(recipient_id=user_id).order_by('-created_at')[:limit]

    def mark_as_read(self, notification_id: int):
        """
        Помечает уведомление как прочитанное
        :param notification_id: ID уведомления
        """
        Notification.objects.filter(id=notification_id).update(is_read=True)

    # Методы для работы с запросами на модерацию
    def get_moderation_requests(self) -> list:
        return Notification.objects.filter(
            type='moderation_request'
        )

    def get_pending_moderations(self) -> list:
        return Notification.objects.filter(
            type='moderation_request',
            status='pending'
        )

    def delete_expired(self, days: int = 30):
        """
        Удаляет устаревшие уведомления
        :param days: Количество дней
        """
        Notification.objects.filter(created_at__lte=timezone.now() - timedelta(days=days)).delete()
