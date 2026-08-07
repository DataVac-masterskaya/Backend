from rest_framework.exceptions import ValidationError


def validate_positive_integer_id(value: str) -> int:
    """Возвращает положительный integer ID или ошибку валидации."""
    if not value.isascii() or not value.isdigit():
        raise ValidationError(
            {'id': 'ID must be a positive integer.'},
        )

    object_id = int(value)
    if object_id <= 0:
        raise ValidationError(
            {'id': 'ID must be a positive integer.'},
        )

    return object_id
