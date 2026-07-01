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

    objects = [model(vaccine_card_version=version, **{**defaults, **item,}) for item in items_data]
    return model.objects.bulk_create(objects)
