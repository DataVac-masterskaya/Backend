from django.core.management.base import BaseCommand

from instructions.tasks import check_official_instructions_updates


class Command(BaseCommand):
    """Ручной синхронный запуск сверки инструкций с источником (без Celery)."""

    help = 'Сверяет сохранённые OfficialInstruction с ГРЛС/ОХЛП и уведомляет админов об изменениях'

    def handle(self, *args, **options):
        check_official_instructions_updates()
        self.stdout.write(self.style.SUCCESS('Проверка завершена.'))
