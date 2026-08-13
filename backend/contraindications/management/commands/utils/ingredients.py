# import csv
import re

from contraindications.management.commands.utils.common import get_version_by_old_id
from reference_books.models import Ingredients
from vaccines.models import IngredientRoleType, VaccineCardVersionIngredient

INGREDIENT_BLOCK_TITLES = (
    r'Действующ\w*\s+веществ\w*',
    r'Вспомогательн\w*\s+веществ\w*',
    r'Адъювант\w*',
    r'Стабилизатор\w*',
    r'Консервант\w*',
    r'Растворител\w*',
    r'Подсластител\w*',
    r'Эмульгатор\w*',
    r'След\w*\s+производств\w*',
    r'Производственн\w*\s+примес\w*',
    r'Остаточн\w*\s+примес\w*',
)
INGREDIENT_BLOCK_TITLE_PATTERN = '|'.join(INGREDIENT_BLOCK_TITLES)

INGREDIENT_BLOCKS_PATTERN = re.compile(
    rf'(?P<title>{INGREDIENT_BLOCK_TITLE_PATTERN})'
    rf'\s*:\s*'
    rf'(?P<content>.*?)'
    rf'(?=\s*(?:{INGREDIENT_BLOCK_TITLE_PATTERN})\s*:|$)',
    flags=re.IGNORECASE | re.DOTALL,
)

ACTIVE_START_MARKERS = ['доза содержит', 'одна доза содержит', 'каждая доза содержит', '1 доза']

ACTIVE_BLOCK_PATTERN = re.compile(
    r"""
    (?P<title>
        одна\s+доза(?:\s*\([^)]*\))?\s+содержит
        |каждая\s+доза(?:\s*\([^)]*\))?\s+содержит
        |доза(?:\s*\([^)]*\))?\s+содержит
        |1\s+доза(?:\s*\([^)]*\))?\s+содержит
    )
    \s*:\s*
    (?P<content>.*?)
    (?=
        \s*(?:перечень\s+)?вспомогательн\w*\s+веществ\w*\s*:
        |$
    )
    """,
    flags=re.IGNORECASE | re.DOTALL | re.VERBOSE,
)


def get_block_type(title):
    """Получает тип текстового блока."""
    title = title.lower()

    if 'действ' in title:
        return 'active'

    if 'адъювант' in title:
        return 'adjuvant'

    if 'стабилизатор' in title:
        return 'stabilizer'

    if 'консервант' in title:
        return 'preservative'

    if 'растворител' in title:
        return 'solvent'

    if 'подсластител' in title:
        return 'sweetener'

    if 'эмульгатор' in title:
        return 'emulsifier'

    if 'след' in title or 'примес' in title:
        return 'production_traces'

    return 'auxiliary'


def extract_ingredient_blocks(text):
    """Получает блоки ингредиентов."""
    blocks = []

    for match in INGREDIENT_BLOCKS_PATTERN.finditer(text):
        blocks.append(
            {
                'type': get_block_type(match.group('title')),
                'content': match.group('content').strip(),
            }
        )

    for match in ACTIVE_BLOCK_PATTERN.finditer(text):
        blocks.append(
            {
                'type': 'active',
                'content': match.group('content').strip(),
            }
        )

    return blocks


def split_ingredients(text):
    """Разделяет блок на ингредиенты по надежным разделителям."""
    ingredients = []
    current = []

    brackets = 0
    i = 0

    while i < len(text):
        char = text[i]

        if char == '(':
            brackets += 1
            current.append(char)
            i += 1
            continue

        if char == ')':
            brackets = max(0, brackets - 1)
            current.append(char)
            i += 1
            continue

        is_bullet = char == '•'
        is_semicolon = char == ';'
        is_comma_space = char == ',' and i + 1 < len(text) and text[i + 1].isspace()

        is_separator = brackets == 0 and (is_bullet or is_semicolon or is_comma_space)

        if is_separator:
            ingredient = ''.join(current).strip(' \n\t.;,:-')

            if ingredient:
                ingredients.append(ingredient)

            current = []

            # Если разделитель ", ", съедаем и пробел после запятой.
            if is_comma_space:
                i += 1
        else:
            current.append(char)

        i += 1

    ingredient = ''.join(current).strip(' \n\t.;,:-')

    if ingredient:
        ingredients.append(ingredient)

    return ingredients


SERVICE_TAIL_PATTERN = re.compile(
    r'\.\s+(?='
    r'[¹²³⁴⁵⁶⁷⁸⁹]'
    r'|Примечание\b'
    r'|Полный перечень\b'
    r'|Перечень\b'
    r'|Препарат\b'
    r'|Вакцина\b'
    r'|Данный препарат\b'
    r'|Состав\b'
    r'|Лиофилизат\b'
    r'|Растворитель\b'
    r')',
    flags=re.IGNORECASE,
)


def cut_service_tail(ingredient):
    """Удаляет служебный текст после названия ингредиента."""
    parts = SERVICE_TAIL_PATTERN.split(ingredient, maxsplit=1)
    return parts[0].strip(' .;:-')


AMOUNT_PATTERN = re.compile(
    r"""
    \s*[—–-]\s*
    (?:
        не\s+более\s+
        |не\s+менее\s+
        |до\s+
        |от\s+
    )?
    [\d.,±×xх<>≤≥\s]+
    (?:
        мкг
        |мг
        |г
        |мл
        |мкл
        |%
        |нг
        |ммоль
        |МЕ
        |ME
        |ЕД
        |ЕС
        |Lf
        |БОЕ
        |ТЦД₅₀
    )
    .*$
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)


def remove_amount(ingredient):
    """Удаляет количество вещества из конца строки."""
    return AMOUNT_PATTERN.sub('', ingredient).strip(' .;:-')


SERVICE_ITEMS = {
    'перечень',
    'лиофилизат',
    'растворитель',
    'препарат с консервантом',
    'препарат без консерванта',
    'вакцина с консервантом',
    'вакцина без консерванта',
    'компонент i',
    'компонент ii',
    'компонент а',
    'компонент б',
}

INGREDIENT_TYPE_BY_BLOCK = {
    'adjuvant': 'Адъювант',
    'stabilizer': 'Стабилизатор',
    'preservative': 'Консервант',
    'sweetener': 'Подсластитель',
    'emulsifier': 'Эмульгатор',
    'production_traces': 'Следы производства',
}

DEFAULT_INGREDIENT_TYPE = 'Не определено'


def is_service_item(ingredient):
    """Проверяет, является ли строка служебным заголовком."""
    normalized = ingredient.strip(' .;:-').lower()
    return normalized in SERVICE_ITEMS


def import_ingredients(wb):
    """Импорт ингредиентов и связи вакцины с ними."""
    ws = wb['ingredients_text']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_id = headers.index('vaccine_id')
    ingredients_text = headers.index('ingredients_text_w/o_html')
    ingredient_count = 0
    ingredients = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccines_id]
        if row[vaccines_id] is None:
            continue
        ingredients_str = row[ingredients_text]
        vaccine_id = int(vaccine_id)
        if ingredients_str is None:
            continue

        vaccine_card_version = get_version_by_old_id(vaccine_id)
        for block in extract_ingredient_blocks(ingredients_str):
            block_type = block['type']
            role = IngredientRoleType.ACTIVE if block_type == 'active' else IngredientRoleType.AUXILIARY

            ingredient_type = INGREDIENT_TYPE_BY_BLOCK.get(
                block_type,
                DEFAULT_INGREDIENT_TYPE,
            )
            for ingredient in split_ingredients(block['content']):
                ingredient = cut_service_tail(ingredient)
                ingredient = remove_amount(ingredient)
                if ingredient is None:
                    continue
                if is_service_item(ingredient):
                    continue
                ingredient, created = Ingredients.objects.get_or_create(
                    name=ingredient,
                    defaults={
                        'type': ingredient_type,
                    },
                )
                VaccineCardVersionIngredient.objects.get_or_create(
                    vaccine_card_version=vaccine_card_version,
                    ingredient=ingredient,
                    defaults={
                        'role': role,
                    },
                )
                if created:
                    ingredient_count += 1
                ingredients.append(ingredient.name)
    ingredients_set = set(ingredients)
    # with open('testset.csv', 'w', newline='', encoding='utf-8-sig') as f:
    #     writer = csv.writer(f)
    #     writer.writerows([[item] for item in ingredients_set])
    return ingredient_count
