import logging
import time

from backend.datavac.celery import app as celery_app


class QueueService:
    """
    Сервис для работы с очередью задач Celery.

    Отвечает за отправку задач в очередь и мониторинг состояния воркеров.
    """

    def __init__(self):
        """
        Инициализация сервиса.

        Создает экземпляр логгера и подключает Celery приложение.
        """
        self.celery = celery_app
        self.logger = logging.getLogger(__name__)

    def enqueue(self, task_name: str, data: dict) -> None:
        """
        Отправляет задачу в очередь Celery.

        :param task_name: Имя задачи для выполнения
        :param data: Данные для задачи в формате словаря
        :raises Exception: Если произошла ошибка при отправке задачи
        """
        try:
            self.celery.send_task(task_name, kwargs=data)
        except Exception as e:
            self.logger.error(f'Ошибка при отправке задачи {task_name}: {str(e)}', extra={'data': data})
            raise

    def get_worker_status(self) -> dict:
        """
        Получает статус воркеров Celery.

        :return: Словарь с информацией о статусе воркеров
        :raises Exception: Если произошла ошибка при получении статуса
        """
        try:
            status = self.celery.control.inspect().ping()
            if not status:
                self.logger.warning('Не удалось получить статус воркеров')
            return status
        except Exception as e:
            self.logger.error(f'Ошибка при проверке статуса воркеров: {str(e)}')
            return None

    def retry_enqueue(self, task_name: str, data: dict, max_retries: int = 3) -> bool:
        """
        Отправляет задачу в очередь с повторными попытками.

        :param task_name: Имя задачи для выполнения
        :param data: Данные для задачи
        :param max_retries: Максимальное число попыток отправки
        :return: True если задача успешно отправлена, False в противном случае
        """
        for attempt in range(max_retries):
            try:
                self.enqueue(task_name, data)
                self.logger.info(f'Задача {task_name} успешно отправлена')
                return True
            except Exception as e:
                self.logger.warning(
                    f'Попытка {attempt + 1}/{max_retries} отправить задачу {task_name} failed: {str(e)}'
                )
                if attempt == max_retries - 1:
                    raise
                self.logger.info('Повторная попытка отправки задачи через 2 секунды')
                time.sleep(2)
