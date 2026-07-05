import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from reference_books.models import (
    Infection,
    CategoryInfection,
    Ingredients
)
from contraindications.models import (
    Contraindication,
    ContraindicationCategory
)


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


# tests/conftest.py
@pytest.fixture
def sample_infections(db):
    category1 = CategoryInfection.objects.create(
        name='virusnye')
    category2 = CategoryInfection.objects.create(
        name='bakterialnye')

    infections = [
        Infection.objects.create(name='Гепатит B', category=category1),
        Infection.objects.create(name='Туберкулез', category=category2),
        Infection.objects.create(name='Корь', category=category1),
        Infection.objects.create(name='Дифтерия', category=category2),
    ]
    return infections


@pytest.fixture
def sample_categories(db):
    """Создает категории противопоказаний"""
    category1 = ContraindicationCategory.objects.create(name='Абсолютные')
    category2 = ContraindicationCategory.objects.create(name='Относительные')
    return [category1, category2]


@pytest.fixture
def sample_contraindications(db, sample_categories):
    """Создает противопоказания с привязкой к категориям"""
    category1, category2 = sample_categories

    contraindication1 = Contraindication.objects.create(
        name='Аллергия на компоненты'
    )
    contraindication1.categories.add(category1)

    contraindication2 = Contraindication.objects.create(
        name='Беременность'
    )
    contraindication2.categories.add(category2)

    return [contraindication1, contraindication2]


@pytest.fixture
def sample_ingredients(db):
    ingredients = [
        Ingredients.objects.create(
            name='Алюминия гидроксид',
            type='Вспомогательное вещество'
        ),
        Ingredients.objects.create(
            name='Анатоксин дифтерийный',
            type='Действующее вещество'
        ),
        Ingredients.objects.create(
            name='Анатоксин столбнячный',
            type='Действующее вещество'
        ),
    ]
    return ingredients
