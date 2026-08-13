from random import randint

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from contraindications.models import Contraindication, ContraindicationCategory
from reference_books.models import Infection, Ingredients
from vaccines.models import VaccineCard, VaccineCardVersion


class Command(BaseCommand):
    help = 'Команда только для тестеров, заполняет поле pregnancy_usage_status согласно ID вакцины'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Эта команда предназначена только для тестовой среды.')
        values = [True, False, None]
        for i, vaccine in enumerate(VaccineCardVersion.objects.all()):
            vaccine.pregnancy_usage_status = values[i % len(values)]
            test_data = 'test' * ((i % 3) + 1)
            vaccine.side_effects = test_data
            vaccine.indications = test_data
            vaccine.schedule_info = test_data
            vaccine.revision_date = vaccine.created_at.date()

            vaccine.save(
                update_fields=[
                    'pregnancy_usage_status',
                    'side_effects',
                    'indications',
                    'schedule_info',
                    'revision_date',
                ]
            )
        for i, vaccine in enumerate(VaccineCard.objects.all()):
            vaccine.search_select_count = randint(1, 100)
            vaccine.popularity = randint(1, 100)
            vaccine.save(update_fields=['search_select_count', 'popularity'])

        for i, ingredient in enumerate(Ingredients.objects.all()):
            ingredient.search_select_count = randint(1, 100)
            ingredient.popularity = randint(1, 100)
            ingredient.save(update_fields=['search_select_count', 'popularity'])

        for i, infection in enumerate(Infection.objects.all()):
            infection.search_select_count = randint(1, 100)
            infection.popularity = randint(1, 100)
            infection.save(update_fields=['search_select_count', 'popularity'])

        category1, _ = ContraindicationCategory.objects.get_or_create(name='Абсолютное')

        category2, _ = ContraindicationCategory.objects.get_or_create(name='Временное')
        for i, contraindication in enumerate(Contraindication.objects.all()):
            contraindication.search_select_count = randint(1, 100)
            if contraindication.pk % 2 == 0:
                contraindication.categories.set([category1])
            else:
                contraindication.categories.set([category2])
            contraindication.save(update_fields=['search_select_count', 'category'])
        self.stdout.write(self.style.SUCCESS('Тестовые значения проставлены.'))
