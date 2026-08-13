from random import randint

from django.core.management.base import BaseCommand

from contraindications.models import Contraindication, ContraindicationCategory
from reference_books.models import Infection, Ingredients
from vaccines.models import VaccineCard, VaccineCardVersion, VaccineCardVersionAdministrationMethod


class Command(BaseCommand):
    help = 'Команда только для тестеров, заполняет поле pregnancy_usage_status согласно ID вакцины'

    def handle(self, *args, **options):
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

        for i, vaccine_method in enumerate(
            VaccineCardVersionAdministrationMethod.objects.all()):
            if vaccine_method.pk % 2 == 0:
                vaccine_method.contraindication_type = 'Временное'
            else:
                vaccine_method.contraindication_type = 'Абсолютное'
            vaccine_method.save(update_fields=['contraindication_type'])

        for i, infection in enumerate(Infection.objects.all()):
            infection.search_select_count = randint(1, 100)
            infection.popularity = randint(1, 100)
            infection.save(update_fields=['search_select_count', 'popularity'])

        category1, _ = ContraindicationCategory.objects.get_or_create(name='Острые заболевания')
        category2, _ = ContraindicationCategory.objects.get_or_create(name='Гиперчувствительность')
        category3, _ = ContraindicationCategory.objects.get_or_create(name='Аллергии')
        category4, _ = ContraindicationCategory.objects.get_or_create(name='Иммунодефициты')
        category5, _ = ContraindicationCategory.objects.get_or_create(name='Острые состояния')

        for i, contraindication in enumerate(Contraindication.objects.all()):
            contraindication.search_select_count = randint(1, 100)
            contraindication.popularity = randint(1, 100)
            i = contraindication.pk % 5
            if i == 0:
                contraindication.categories.set([category1])
                if contraindication.pk % 2 == 0:
                    contraindication.subcategory = 'Заболевания сердца'
                else:
                    contraindication.subcategory = 'Заболевания почек'
            elif i == 1:
                contraindication.categories.set([category2])
            elif i == 2:
                contraindication.categories.set([category3])
                contraindication.subcategory = 'Аллергии'
            elif i == 3:
                contraindication.categories.set([category4])
            else:
                contraindication.categories.set([category5])
            contraindication.save(update_fields=['search_select_count', 'popularity', 'subcategory'])
        self.stdout.write(self.style.SUCCESS('Тестовые значения проставлены.'))
