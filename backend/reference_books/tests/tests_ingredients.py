from django.core.exceptions import ValidationError

import pytest

from reference_books.models import Ingredients


# Фикстура для создания базового объекта
@pytest.fixture
def ingredient():
    return Ingredients.objects.create(
        name='Гидроксид алюминия',
        type='adjuvant',
        description='Описание ингредиента'
    )


# Тест создания валидного объекта
def test_valid_ingredient_creation(ingredient):
    assert ingredient.name == 'Гидроксид алюминия'
    assert ingredient.type == 'adjuvant'
    assert ingredient.description == 'Описание ингредиента'


# Тест обязательных полей
def test_required_fields():
    with pytest.raises(ValidationError):
        Ingredients.objects.create(type='adjuvant')  # отсутствует name

    with pytest.raises(ValidationError):
        Ingredients.objects.create(name='Тестовое')  # отсутствует type


# Тест максимальной длины поля name
def test_name_max_length():
    max_length = Ingredients._meta.get_field('name').max_length
    long_name = 'a' * (max_length + 1)

    with pytest.raises(ValidationError):
        Ingredients.objects.create(
            name=long_name,
            type='adjuvant'
        )


# Тест валидности типа
@pytest.mark.parametrize('ingredient_type', ['adjuvant', 'stabilizer', 'active'])
def test_type_validation(ingredient_type):
    ingredient = Ingredients.objects.create(
        name='Тестовое',
        type=ingredient_type,
        description='Тест'
    )
    assert ingredient.type == ingredient_type


# Тест уникальности названия
def test_unique_name(ingredient):
    with pytest.raises(ValidationError):
        Ingredients.objects.create(
            name=ingredient.name,
            type='adjuvant'
        )


# Тест метода __str__
def test_str_method(ingredient):
    assert str(ingredient) == ingredient.name


# Тест необязательности поля description
def test_description_optional():
    ingredient = Ingredients.objects.create(
        name='Тестовое',
        type='adjuvant'
    )
    assert ingredient.description is None


# Тест валидации типа
def test_invalid_type():
    with pytest.raises(ValidationError):
        Ingredients.objects.create(
            name='Тестовое',
            type='неверный_тип'
        )
