from datetime import timedelta

from django.utils import timezone

from notifications.models import Notification


class NotificationRepository:
    """
    Репозиторий для работы с уведомлениями.

    Отвечает за CRUD-операции и специализированные запросы к уведомлениям.
    """

    def save(self, notification_data: dict) -> Notification:
        """
        Сохраняет новое уведомление в базе данных.

        :param notification_data: Данные уведомления для сохранения
        :return: Созданный объект уведомления.
        """
        return Notification.objects.create(**notification_data)

    def get_by_id(self, notification_id: int) -> Notification:
        """
        Получает уведомление по его ID.

        :param notification_id: Уникальный идентификатор уведомления
        :return: Объект уведомления
        :raises: Notification.DoesNotExist если уведомление не найдено.
        """
        return Notification.objects.get(id=notification_id)

    def get_user_notifications(self, user_id: int, limit: int = 10) -> list:
        """
        Возвращает список уведомлений для указанного пользователя.

        :param user_id: ID пользователя
        :param limit: Максимальное количество возвращаемых уведомлений
        :return: Список объектов уведомлений.
        """
        return Notification.objects.filter(recipient_id=user_id).order_by('-created_at')[:limit]

    def mark_as_read(self, notification_id: int) -> None:
        """
        Помечает уведомление как прочитанное.

        :param notification_id: ID уведомления для отметки.
        """
        Notification.objects.filter(id=notification_id).update(is_read=True)

    def get_moderation_requests(self) -> list:
        """
        Возвращает все запросы на модерацию.

        :return: Список объектов уведомлений типа moderation_request.
        """
        return Notification.objects.filter(type='moderation_request')

    def get_pending_moderations(self) -> list:
        """
        Возвращает ожидающие модерации уведомления.

        :return: Список объектов уведомлений в статусе pending.
        """
        return Notification.objects.filter(type='moderation_request', status='pending')

    def delete_expired(self, days: int = 30) -> None:
        """
        Удаляет устаревшие уведомления.

        :param days: Количество дней для определения устаревших уведомлений.
        """
        Notification.objects.filter(created_at__lte=timezone.now() - timedelta(days=days)).delete()
