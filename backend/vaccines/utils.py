from rest_framework import serializers


def validate_exists(model, id_value, error_message):
    """Проверяет существование объекта в БД по ID."""
    if not model.objects.filter(id=id_value).exists():
        raise serializers.ValidationError(error_message)
    return id_value


def bulk_create_relations(version, model, items_data, defaults=None):
    """Создает связи через промежуточную модель с помощью bulk_create."""
    if not items_data:
        return []

    defaults = defaults or {}

    objects = [
        model(
            vaccine_card_version=version,
            **{
                **defaults,
                **item,
            },
        )
        for item in items_data
    ]
    return model.objects.bulk_create(objects)


def format_age(months):
    """Форматирует возраст в месяцах в читаемую строку."""
    if months is None:
        return None
    if months == 0:
        return '0 дней'
    if months == 1:
        return '1 месяца'
    if months % 12 == 0:
        years = months // 12
        if years == 1:
            return f'{years} год'
        elif 2 <= years <= 4:
            return f'{years} года'
        else:
            return f'{years} лет'
    return f'{months} месяцев'
