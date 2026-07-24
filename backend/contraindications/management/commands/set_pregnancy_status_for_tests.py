from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from vaccines.models import VaccineCardVersion


class Command(BaseCommand):
    help = 'Команда только для тестеров, заполняет поле pregnancy_usage_status согласно ID вакцины'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Эта команда предназначена только для тестовой среды.')
        values = [True, False, None]
        for i, vaccine in enumerate(VaccineCardVersion.objects.all()):
            vaccine.pregnancy_usage_status = values[i % len(values)]
            vaccine.save(update_fields=['pregnancy_usage_status'])

        self.stdout.write(self.style.SUCCESS('Тестовые значения успешно проставлены.'))
