class NotificationService:
    def __init__(self, repo: NotificationRepository, queue: QueueService):
        self.repo = repo
        self.queue = queue

    def send_notification(self, notification_data):
        # Сохраняем уведомление в БД
        notification = self.repo.save(notification_data)

        # Отправляем задачу в очередь
        self.queue.enqueue(
            'tasks.email_tasks.send_email_notification',
            {'notification_id': notification.id}
        )
