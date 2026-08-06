from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook

from contraindications.management.commands.utils.common import clean_text, get_sheet, get_version_by_old_id
from contraindications.management.commands.utils.ingredients import import_ingredients
from contraindications.management.commands.utils.vaccines import (
    import_vaccine_interaction,
    import_vaccine_pregnancy_use,
    import_vaccine_simult_administration,
    import_vaccine_storage,
    import_vaccines,
    set_vaccine_ages,
    set_vaccine_nonspec_links,
)
from contraindications.models import Contraindication
from reference_books.models import (
    CategoryInfection,
    Infection,
    MethodsOfAdministration,
)
from vaccines.constants import AGES_MAP
from vaccines.models import (
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
    VaccineCardVersionInfection,
)


def import_contraindications(wb):
    """Импорт противопоказаний."""
    ws = get_sheet(wb, 'contraindications_list')
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    name_idx = headers.index('contraindication_name')
    id_idx = headers.index('contraindication_ID')
    count_add = 0
    seen_ids = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        contraindication_name = row[name_idx]
        old_id = row[id_idx]

        if old_id is None:
            raise CommandError('В файле обнаружена строка без contraindication_ID.')
        if contraindication_name is None:
            raise CommandError(f'Для contraindication_ID={old_id} отсутствует название.')
        if old_id in seen_ids:
            raise CommandError(
                'В файле обнаружен элемент с повторяющимся '
                f'contraindication_ID: {old_id}, '
                f'contraindication_name: {contraindication_name}'
            )

        seen_ids.add(old_id)
        _, created = Contraindication.objects.update_or_create(
            old_id=old_id,
            defaults={
                'name': contraindication_name,
            },
        )
        if created:
            count_add += 1
    return count_add


CATEGORY_MAP = {
    'национальный календарь': 'national',
    'сверх календаря': 'additional',
    'другие': 'others',
}


def import_infection_categories(wb):
    """Импорт категорий инфекций."""
    ws = get_sheet(wb, 'infections_list')
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    category_idx = headers.index('calendar')
    id_idx = headers.index('infection_id')
    count_add = 0
    seen_categories = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        category = row[category_idx]
        if row[id_idx] is None:
            continue
        category = clean_text(category)
        category = CATEGORY_MAP[category]
        if category in seen_categories:
            continue
        seen_categories.add(category)
        _, created = CategoryInfection.objects.get_or_create(
            name=category,
        )
        if created:
            count_add += 1
    return count_add


def import_infections(wb):
    """Импорт инфекций."""
    ws = wb['infections_list']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    name_idx = headers.index('infection_name')
    id_idx = headers.index('infection_id')
    category_idx = headers.index('calendar')
    count_add = 0
    seen_ids = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[id_idx] is None:
            continue
        infection_name = row[name_idx]
        old_id = row[id_idx]
        category = row[category_idx]
        category = clean_text(category)
        category = CATEGORY_MAP[category]
        if old_id is None:
            raise CommandError('В файле обнаружена строка без infection_id.')
        if infection_name is None:
            raise CommandError(f'Для infection_id={old_id} отсутствует название.')
        if old_id in seen_ids:
            raise CommandError(
                f'В файле обнаружен элемент с повторяющимся infection_id: {old_id}, infection_name: {infection_name}'
            )
        if category is None:
            raise CommandError(f'Для infection_id={old_id} отсутствует категория.')

        seen_ids.add(old_id)
        category_infection = CategoryInfection.objects.get(name=category)
        _, created = Infection.objects.update_or_create(
            old_id=old_id,
            defaults={
                'name': infection_name,
                'category': category_infection,
            },
        )
        if created:
            count_add += 1
    return count_add


def import_methods_of_administration(wb):
    """Импорт методов введения вакцин."""
    ws = get_sheet(wb, 'routes_of_administration_list')
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    name_idx = headers.index('route_of_administration_name')
    id_idx = headers.index('route_of_administration_ID')
    image_link_google_drive_idx = headers.index('image_link_Google_Drive')
    icon_link_google_drive_idx = headers.index('icon_link_Google_Drive')

    count_add = 0
    seen_ids = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        route_name = row[name_idx]
        old_id = row[id_idx]
        icon_link_google_drive = row[icon_link_google_drive_idx]
        image_link_google_drive = row[image_link_google_drive_idx]
        if old_id is None:
            raise CommandError('В файле обнаружена строка без route_of_administration_ID.')
        if route_name is None:
            raise CommandError(f'Для route_of_administration_ID={old_id} отсутствует название.')
        if old_id in seen_ids:
            raise CommandError(
                'В файле обнаружен элемент с повторяющимся '
                f'route_of_administration_ID: {old_id}, '
                f'route_of_administration_name: {route_name}'
            )

        seen_ids.add(old_id)
        _, created = MethodsOfAdministration.objects.update_or_create(
            old_id=old_id,
            defaults={
                'name': route_name,
                'list_icon_url': icon_link_google_drive,
                'detail_image_url': image_link_google_drive,
            },
        )
        if created:
            count_add += 1
    return count_add


def import_vaccine_version_infections(wb):
    """Импорт связи вакцины и инфекций."""
    ws = wb['vaccines_infections']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_ids = headers.index('vaccine_ID')
    infections_ids = headers.index('infection_ID')
    count = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccines_ids]
        if vaccine_id is None:
            continue
        infection_id = row[infections_ids]
        vaccine_id = int(vaccine_id)
        if infection_id is None:
            continue
        infection = Infection.objects.get(old_id=infection_id)
        vaccine_card_version = get_version_by_old_id(vaccine_id)
        _, created = VaccineCardVersionInfection.objects.get_or_create(
            vaccine_card_version=vaccine_card_version, infection=infection
        )
        if created:
            count += 1
    return count


def import_vaccine_version_contraindications(wb):
    """Импорт связи вакцины и противопоказаний."""
    ws = wb['vaccines_contraindications']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_ids = headers.index('vaccine_ID')
    contraindications_ids = headers.index('contraindication_ID')
    count = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccines_ids]
        if vaccine_id is None:
            continue
        contraindication_id = row[contraindications_ids]
        vaccine_id = int(vaccine_id)
        if contraindication_id is None:
            continue
        contraindication = Contraindication.objects.get(old_id=contraindication_id)
        vaccine_card_version = get_version_by_old_id(vaccine_id)
        _, created = VaccineCardVersionContraindication.objects.get_or_create(
            vaccine_card_version=vaccine_card_version, contraindication=contraindication
        )
        if created:
            count += 1
    return count


def import_vaccine_version_administration_methods(wb):
    """Импорт связи вакцины и методов введения."""
    ws = wb['vaccines_routes_of_administrati']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_ids = headers.index('vaccine_ID')
    routes_ids = headers.index('route_of_administration_ID')
    notes = headers.index('pop_up_comment_text_route_of_administration')
    ages_from = headers.index('age_from_value')
    ages_to = headers.index('age_through_value')
    count = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccines_ids]
        if vaccine_id is None:
            continue
        route_id = row[routes_ids]
        vaccine_id = int(vaccine_id)
        note = row[notes]
        age_from = row[ages_from]
        age_to = row[ages_to]
        age_from = clean_text(age_from)
        age_to = clean_text(age_to)
        age_from = AGES_MAP[age_from]
        age_to = AGES_MAP[age_to]
        if route_id is None:
            continue
        administration_method = MethodsOfAdministration.objects.get(old_id=route_id)
        vaccine_card_version = get_version_by_old_id(vaccine_id)
        _, created = VaccineCardVersionAdministrationMethod.objects.get_or_create(
            vaccine_card_version=vaccine_card_version,
            administration_method=administration_method,
            note=note,
            age_from=age_from,
            age_to=age_to,
        )
        if created:
            count += 1
    return count


class Command(BaseCommand):
    help = 'Импортирует противопоказания из указанного excel-файла со страницы contraindications_list'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Путь к excel-файлу')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
            try:
                with transaction.atomic():
                    count = import_contraindications(wb)
                    self.stdout.write(f'Импорт противопоказаний завершён. Добавлено: {count}.')
                    count = import_infection_categories(wb)
                    self.stdout.write(f'Импорт категорий инфекций завершён. Добавлено: {count}.')
                    count = import_infections(wb)
                    self.stdout.write(f'Импорт инфекций завершён. Добавлено: {count}.')
                    count = import_methods_of_administration(wb)
                    self.stdout.write(f'Импорт методов введения завершён. Добавлено: {count}.')
                    count = import_vaccines(wb)
                    self.stdout.write(f'Импорт вакцин завершён. Добавлено: {count}.')
                    count = import_ingredients(wb)
                    self.stdout.write(f'Импорт ингредиентов завершён. Добавлено: {count}.')
                    count = import_vaccine_storage(wb)
                    self.stdout.write(f'Импорт условий хранения завершен, обновлено: {count}.')
                    count = import_vaccine_pregnancy_use(wb)
                    self.stdout.write(f'Импорт использования при беременности завершен, обновлено: {count}.')
                    count = import_vaccine_interaction(wb)
                    self.stdout.write(f'Импорт взаимодействия с другими лекарствами завершен, обновлено: {count}.')
                    count = import_vaccine_simult_administration(wb)
                    self.stdout.write(f'Импорт взаимодействия с другими вакцинами завершен, обновлено: {count}.')
                    count = import_vaccine_version_infections(wb)
                    self.stdout.write(f'Импорт связи версии карточки вакцины и инфекции завершен, добавлено: {count}.')
                    count = import_vaccine_version_contraindications(wb)
                    self.stdout.write(
                        f'Импорт связи версии карточки вакцины и противопоказания завершен, добавлено: {count}.'
                    )
                    count = import_vaccine_version_administration_methods(wb)
                    self.stdout.write(
                        f'Импорт связи версии карточки вакцины и способов введения завершен, добавлено: {count}.'
                    )
                    count = set_vaccine_ages(wb)
                    self.stdout.write(f'Возраста использования вакцин обновлены, добавлено: {count}.')
                    count = set_vaccine_nonspec_links(wb)
                    self.stdout.write(f'Ссылки для неспециалистов обновлены, добавлено: {count}.')
            except Exception as e:
                raise CommandError(e)
        finally:
            wb.close()
