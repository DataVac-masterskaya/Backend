import csv
import re

from contraindications.management.commands.utils.common import clean_text, get_version_by_old_id
from reference_books.models import Ingredients
from vaccines.models import VaccineCardVersionIngredient

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

ACTIVE_START_MARKERS = ['доза содержит', 'одна доза содержит', 'каждая доза содержит', '1 доза']


def extract_ingredient_blocks(text):
    """Выделяет из строки смысловые блоки."""
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


def split_ingredients(text):
    """Разделяет блок на отдельные ингредиенты."""
    ingredients = []
    current = []
    brackets = 0

    for i, char in enumerate(text):
        if char == '(':
            brackets += 1
        elif char == ')':
            brackets -= 1

        is_decimal = char == ',' and i > 0 and i < len(text) - 1 and text[i - 1].isdigit() and text[i + 1].isdigit()

        is_separator = char == '•' or (char == ',' and not is_decimal)

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


def import_ingredients(wb):
    """Импорт ингредиентов и связи вакцины с ними."""
    ws = wb['ingredients_text']
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccines_id = headers.index('vaccine_id')
    ingredients_text = headers.index('ingredients_text_w/o_html')
    ingredient_count = 0
    suspicious = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccines_id]
        if row[vaccines_id] is None:
            continue
        ingredients_str = row[ingredients_text]
        vaccine_id = int(vaccine_id)
        if ingredients_str is None:
            continue
        ingredients_blocks = extract_ingredient_blocks(ingredients_str)
        vaccine_card_version = get_version_by_old_id(vaccine_id)
        for ingredient_type, block in ingredients_blocks.items():
            block = clean_text(block)
            for ingredient in split_ingredients(block):
                if '. ' in ingredient:
                    suspicious.append(ingredient)
                ingredient, created = Ingredients.objects.get_or_create(name=ingredient)
                VaccineCardVersionIngredient.objects.get_or_create(
                    vaccine_card_version=vaccine_card_version,
                    ingredient=ingredient,
                    defaults={
                        'role': ingredient_type,
                    },
                )
                if created:
                    ingredient_count += 1
    with open('column.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows([[item] for item in suspicious])
    return ingredient_count
