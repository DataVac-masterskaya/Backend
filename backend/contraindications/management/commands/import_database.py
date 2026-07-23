import re

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook

from contraindications.models import Contraindication, ContraindicationCategory
from reference_books.models import (CategoryInfection,
                                    Infection,
                                    Ingredients,
                                    )
from vaccines.models import (VaccineCard, VaccineCardStatus, VaccineCardVersion,
                             VaccineCardVersionAdministrationMethod,
                             VaccineCardVersionContraindication,
                             VaccineCardVersionInfection,
                             VaccineCardVersionIngredient,
                             VersionStatus, Age)

from datavac.constants import AGES_MAP, STOP_PHRASES

User = get_user_model()

INGREDIENT_BLOCKS_PATTERN = re.compile(
    r'(?P<title>'
    r'Действующ\w*\s+веществ\w*'
    r'|Вспомогательн\w*\s+веществ\w*'
    r'|Адъювант\w*'
    r')\s*:\s*'
    r'(?P<content>.*?)(?='
    r'\s*(?:Действующ\w*\s+веществ\w*'
    r'|Вспомогательн\w*\s+веществ\w*'
    r'|Адъювант\w*)\s*:|$)',
    flags=re.IGNORECASE | re.DOTALL,
)

ACTIVE_START_MARKERS = [
    'доза содержит',
    'одна доза содержит',
    'каждая доза содержит',
    '1 доза'
]

def extract_ingredient_blocks(text):
    blocks = {}

    for match in INGREDIENT_BLOCKS_PATTERN.finditer(text):
        title = match.group('title').lower()
        content = match.group('content').strip()

        if 'действ' in title:
            key = 'active'
        elif 'вспом' in title:
            key = 'auxiliary'
        elif 'адъювант' in title:
            key = 'adjuvant'
        else:
            continue

        blocks[key] = content

    return blocks

def clean_ingredient_text(ingredients):
    ingredients = ingredients.replace('\xa0', ' ')
    ingredients = ' '.join(ingredients.split())
    ingredients = ingredients.strip(' .;,:-')
    return ingredients

def split_ingredients(text):
    ingredients = []
    current = []
    brackets = 0

    for i, char in enumerate(text):
        if char == '(':
            brackets += 1
        elif char == ')':
            brackets -= 1

        is_decimal = (
            char == ','
            and i > 0
            and i < len(text) - 1
            and text[i - 1].isdigit()
            and text[i + 1].isdigit()
        )

        is_separator = (
            char == '•'
            or (char == ',' and not is_decimal)
        )

        if is_separator and brackets == 0:
            ingredient = ''.join(current).strip(' .;:-')
            if ingredient:
                ingredients.append(ingredient)
            current = []
        else:
            current.append(char)

    ingredient = ''.join(current).strip(' .;:-')
    if ingredient:
        ingredients.append(ingredient)

    return ingredients

def get_sheet(workbook, name):
    """Получение листа таблицы."""
    try:
        return workbook[name]
    except KeyError:
        raise CommandError(f'Лист "{name}" не найден')

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

def import_infection_categories(wb):
    """Импорт категорий инфекций."""
    ws = get_sheet(wb, 'infections_list')
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    category_idx = headers.index('calendar')
    count_add = 0
    seen_categories = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        category = row[category_idx]
        if category in seen_categories:
            continue
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
        infection_name = row[name_idx]
        old_id = row[id_idx]
        category = row[category_idx]

        if old_id is None:
            raise CommandError('В файле обнаружена строка без infection_id.')
        if infection_name is None:
            raise CommandError(f'Для infection_id={old_id} отсутствует название.')
        if old_id in seen_ids:
            raise CommandError(
                'В файле обнаружен элемент с повторяющимся '
                f'infection_id: {old_id}, '
                f'infection_name: {infection_name}'
            )
        if category is None:
            raise CommandError(
                f'Для infection_id={old_id} отсутствует категория.'
            )

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

def import_ingredients(wb):
    ws = wb['ingredients_text']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_id = headers.index('vaccine_id')
    ingredients_text = headers.index('ingredients_text_w/o_html')
    try:
        with transaction.atomic():
            for row in ws.iter_rows(min_row=2, values_only=True):
                vaccine_id = int(row[vaccines_id])
                ingredients_str = row[ingredients_text]
                if vaccine_id is None:
                    raise CommandError('В файле обнаружена строка без vaccine_id.')
                if ingredients_str is None:
                    continue
                ingredients_blocks = extract_ingredient_blocks(ingredients_str)
                for ingredient_type, block in ingredients_blocks.items():
                    block = clean_ingredient_text(block)
                    for ingredient in split_ingredients(block):
                        ingredient_count += 1
                        # Ingredients.objects.get_or_create(
                        #     name=ingredient,
                        #     type=ingredient_type,
                        # )
                        print(f' {vaccine_id} - {ingredient_type}: {ingredient}')
    finally:
        print(ingredient_count)
        wb.close()

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
        _, created = Contraindication.objects.update_or_create(
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

# def import_ages(wb):
#     ws1 = get_sheet(wb, 'ages_from_list')
#     ws2 = get_sheet(wb, 'ages_through_list')
#     headers1 = [cell.value for cell in next(ws1.iter_rows(min_row=1, max_row=1))]
#     headers2 = [cell.value for cell in next(ws2.iter_rows(min_row=1, max_row=1))]

#     id_idx = headers1.index('age_from_id')
#     age_value_idx = headers1.index('age_from_value')
#     count_add = 0
#     seen_ages = set()
    
#     for row in ws1.iter_rows(min_row=2, values_only=True):
#         old_id = row[id_idx]
#         age_value = row[age_value_idx]
#         if age_value in seen_ages:
#             continue
#         seen_ages.add(age_value)
#         _, created = Age.objects.update_or_create(
#             value = age_value,
#             defaults={
#                 'old_from_age_id': old_id,
#             },
#         )
#         if created:
#             count_add += 1
    
#     id_idx = headers2.index('age_through_id')
#     age_value_idx = headers2.index('age_through_value')
#     for row in ws2.iter_rows(min_row=2, values_only=True):
#         old_id = row[id_idx]
#         age_value = row[age_value_idx]
#         if age_value in seen_ages:
#             _, created = Age.objects.update_or_create(
#                 value = age_value,
#                 defaults={
#                     'old_through_age_id': old_id,
#                 },
#             )
#         seen_ages.add(age_value)
#         _, created = Age.objects.update_or_create(
#             value = age_value,
#             defaults={
#                 'old_through_age_id': old_id,
#             },
#         )
#         if created:
#             count_add += 1
#     return count_add


def get_age(age_str):
    """Соответствие возрастов из легаси в количество дней. Используется только при одноразовой миграции данных."""
    age_str = age_str.replace('\xa0', ' ').strip()
    age = AGES_MAP.get(age_str)
    if age_str not in AGES_MAP:
        raise CommandError(f'Неизвестное значение возраста: "{age_str}"')
    return age
    
def import_vaccines(wb, system_user):
    """Импорт карточек и версий вакцин."""
    ws1 = get_sheet(wb, 'vaccines')
    ws2 = get_sheet(wb, 'vaccines_ages')
    headers1 = [cell.value for cell in next(ws1.iter_rows(min_row=1, max_row=1))]
    headers2 = [cell.value for cell in next(ws2.iter_rows(min_row=1, max_row=1))]
    id_idx = headers1.index('id')
    short_name_idx = headers1.index('short_name')
    longe_name_idx = headers1.index('long_name')
    manufacturer_idx = headers1.index('manufacturer')
    in_use_in_Russia_idx = headers1.index('in_use_in_Russia')
    comment_to_show_wo_html_idx = headers1.index('comment_to_show_wo_html')

    count_add = 0
    for row1 in ws1.iter_rows(min_row=2, values_only=True):
        vaccine_id = row1[id_idx]
        name = row1[short_name_idx]
        official_name = row1[longe_name_idx]
        manufacturer = row1[manufacturer_idx]
        in_use_in_Russia = row1[in_use_in_Russia_idx]
        comment_to_show_wo_html = row1[comment_to_show_wo_html_idx]
        card = VaccineCard.objects.create(
            status=VaccineCardStatus.ACTIVE,
            is_visible=True,
            created_by=system_user,
            updated_by=system_user,
        )
        version = VaccineCardVersion.objects.create(
            vaccine_card=card,
            version_number=1,
            version_status=VersionStatus.DRAFT,
            moderation_request=1,
            name=name,
            official_name=official_name,
            description=,
            manufacturer=manufacturer,
            is_available_in_rf=in_use_in_Russia,
            min_age=,
            max_age=,
            pregnancy_usage_status=,
            storage_conditions=,
            interaction_info=,
            compatibility_info=,
            schedule_info=,
            side_effects=,
            indications=,
            registration_date=,
            revision_date=,
            ohlp_url=,
            nonspec_url=,
            instruction_url=,
            comment_source=comment_to_show_wo_html,
            comment_ANO=,
            created_by=system_user,
            approved_by=system_user,
        )
        count_add += 1
    return count_add


class Command(BaseCommand):
    help = 'Импортирует противопоказания из указанного excel-файла со страницы contraindications_list'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Путь к excel-файлу')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        system_user=User.object.get(username='admin')
        try:
            wb = load_workbook(file_path, read_only=True)
            try:
                with transaction.atomic():
                    count = import_contraindications(wb)
                    self.stdout.write(
                        f'Импорт противопоказаний завершён. Добавлено: {count}.'
                    )
                    count = import_infection_categories(wb)
                    self.stdout.write(
                        f'Импорт категорий инфекций завершён. Добавлено: {count}.'
                    )
                    count = import_infections(wb)
                    self.stdout.write(
                        f'Импорт инфекций завершён. Добавлено: {count}.'
                    )

                    count = import_methods_of_administration(wb)
                    self.stdout.write(
                        f'Импорт методов введения завершён. Добавлено: {count}.'
                    )
                    # count = import_ages(wb)
                    # self.stdout.write(
                    #     f'Импорт возможных возрастов завершён. Добавлено: {count}.'
                    # )
                    import_vaccines(wb, system_user)
                    count = import_ingredients(wb)
                    self.stdout.write(
                        f'Импорт ингредиентов завершён. Добавлено: {count}.'
                    )
                    import_vaccine_version_infections(wb)
                    import_vaccine_version_contraindications(wb)
                    # import_vaccine_version_ingredients(wb)
                    import_vaccine_version_administration_methods(wb)

                    set_current_versions(wb)
        finally:
            wb.close()
