class NotificationService:
    def __init__(self, repo: NotificationRepository, queue: QueueService):
        self.repo = repo
        self.queue = queue

    # Уведомления о создании карточки
    def send_card_created(self, card: VaccineCard, creator: User):
        self._send_notification(
            card.id,
            'card_created',
            creator.id,
            {
                'card_name': card.name,
                'created_by': creator.id
            }
        )

    # Уведомления об изменениях
    def send_card_updated(self, card: VaccineCard, editor: User):
        self._send_notification(
            card.id,
            'card_updated',
            editor.id,
            {
                'card_name': card.name,
                'changes': card.get_changes()
            }
        )

    # Уведомления о модерации
    def send_moderation_request(self, card: VaccineCard):
        admins = User.objects.filter(role='admin')
        for admin in admins:
            self._send_notification(
                card.id,
                'moderation_request',
                admin.id,
                {
                    'card_name': card.name,
                    'request_id': card.moderation_id
                }
            )

# Уведомления об одобрении
    def send_moderation_approved(self, card: VaccineCard, admin: User):
        editors = card.editors.all()
        for editor in editors:
            self._send_notification(
                card.id,
                'moderation_approved',
                editor.id,
                {
                    'card_name': card.name,
                    'approved_by': admin.id
                }
            )

    # Уведомления об отклонении
    def send_moderation_rejected(self, card: VaccineCard, admin: User, reason: str):
        editors = card.editors.all()
        for editor in editors:
            self._send_notification(
                card.id,
                'moderation_rejected',
                editor.id,
                {
                    'card_name': card.name,
                    'rejected_by': admin.id,
                    'reason': reason
                }
            )

# Внутренние методы
    def _send_notification(self, entity_id, type, recipient_id, data):
        notification = {
            'entity_id': entity_id,
            'type': type,
            'recipient_id': recipient_id,
            'data': data
        }
        self.repo.save(notification)
        self.queue.enqueue('send_notification', notification)

    # Уведомления о скрытых карточках
    def send_card_hidden(self, card: VaccineCard, admin: User):
        self._send_notification(
            card.id,
            'card_hidden',
            admin.id,
            {
                'card_name': card.name,
                'hidden_by': admin.id,
                'comment': card.hidden_comment
            }
        )

    # Уведомления об удаленных карточках
    def send_card_deleted(self, card: VaccineCard, admin: User):
        self._send_notification(
            card.id,
            'card_deleted',
            admin.id,
            {
                'card_name': card.name,
                'deleted_by': admin.id,
                'comment': card.delete_comment
            }
        )

    # Уведомления о восстановлении карточек
    def send_card_restored(self, card: VaccineCard, admin: User):
        self._send_notification(
            card.id,
            'card_restored',
            admin.id,
            {
                'card_name': card.name,
                'restored_by': admin.id,
                'comment': card.restore_comment
            }
        )

    # Уведомления об ошибках валидации
    def send_validation_error(self, card: VaccineCard, errors: dict):
        editors = card.editors.all()
        for editor in editors:
            self._send_notification(
                card.id,
                'validation_error',
                editor.id,
                {
                    'card_name': card.name,
                    'errors': errors
                }
            )
