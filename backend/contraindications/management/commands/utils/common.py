from django.core.management.base import CommandError

from vaccines.models import VaccineCardVersion


def clean_text(ingredients):
    """Чистит строку от лишних символов."""
    ingredients = ingredients.replace('\xa0', ' ')
    ingredients = ' '.join(ingredients.split())
    ingredients = ingredients.strip(' .;,:-')
    return ingredients


def get_version_by_old_id(old_id):
    """Получение карточки версии вакцины по старому ID."""
    return VaccineCardVersion.objects.get(old_id=old_id)


def get_sheet(workbook, name):
    """Получение листа таблицы."""
    try:
        return workbook[name]
    except KeyError:
        raise CommandError(f'Лист "{name}" не найден')


TRUE_VALUES = {
    'in use',
}

FALSE_VALUES = {
    'not in use',
}


def bool_usage(value):
    """Преобразование текстового значения использования в булево."""
    if value is None:
        raise CommandError('Не указано значение поля "in_use_in_Russia".')
    value = str(value)
    value = value.replace('\n', ' ')
    value = ' '.join(value.split())
    value = value.strip().lower()
    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False
    else:
        raise CommandError(f'Значение "{value}" не распознано.')
