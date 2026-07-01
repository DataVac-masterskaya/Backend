from celery import Celery
from config.settings import CELERY_BROKER_URL


class QueueService:
    def __init__(self):
        self.celery = Celery('notifications', broker=CELERY_BROKER_URL)
        self.celery.conf.update(
            result_backend=CELERY_BROKER_URL,
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            task_ignore_result=True,
            task_time_limit=300,
            task_retry_backoff=True,
            task_max_retries=5
        )

    def enqueue(self, task_name, data):
        """Помещает задачу в очередь"""
        self.celery.send_task(task_name, kwargs=data)

    def get_worker_status(self):
        """Получает статус воркеров"""
        return self.celery.control.inspect().ping()
