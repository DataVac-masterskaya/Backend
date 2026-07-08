from django.contrib.auth import get_user_model
from repositories.notification_repository import NotificationRepository
from services.queue_service import QueueService

from vaccines.models import VaccineCard

User = get_user_model()


class NotificationService:
    def __init__(self, repo: NotificationRepository, queue: QueueService):
        """Инициализирует сервис уведомлений.

        Args:
            repo: Репозиторий для работы с уведомлениями.
            queue: Сервис очереди для отправки уведомлений.
        """
        self.repo = repo
        self.queue = queue

    # Уведомления о создании карточки
    def send_card_created(self, card: VaccineCard, creator):
        self._send_notification(card.id, 'card_created', creator.id, {'card_name': card.name, 'created_by': creator.id})

    # Уведомления об изменениях
    def send_card_updated(self, card: VaccineCard, editor):
        self._send_notification(
            card.id, 'card_updated', editor.id, {'card_name': card.name, 'changes': card.get_changes()}
        )

    # Уведомления о модерации
    def send_moderation_request(self, card: VaccineCard):
        admins = User.objects.filter(role='admin')
        for admin in admins:
            self._send_notification(
                card.id, 'moderation_request', admin.id, {'card_name': card.name, 'request_id': card.moderation_id}
            )

    # Уведомления об одобрении
    def send_moderation_approved(self, card: VaccineCard, admin):
        editors = card.editors.all()
        for editor in editors:
            self._send_notification(
                card.id, 'moderation_approved', editor.id, {'card_name': card.name, 'approved_by': admin.id}
            )

    # Уведомления об отклонении
    def send_moderation_rejected(self, card: VaccineCard, admin, reason: str):
        editors = card.editors.all()
        for editor in editors:
            self._send_notification(
                card.id,
                'moderation_rejected',
                editor.id,
                {'card_name': card.name, 'rejected_by': admin.id, 'reason': reason},
            )

    # Внутренние методы
    def _send_notification(self, entity_id, type, recipient_id, data):
        notification = {'entity_id': entity_id, 'type': type, 'recipient_id': recipient_id, 'data': data}
        self.repo.save(notification)
        self.queue.enqueue('send_notification', notification)

    # Метод для получения уведомлений пользователя
    def get_user_notifications(self, user_id: int, limit: int = 10):
        return self.repo.get_by_recipient(user_id, limit)

    # Метод для отметки уведомления как прочитанного
    def mark_as_read(self, notification_id: int):
        self.repo.mark_as_read(notification_id)
