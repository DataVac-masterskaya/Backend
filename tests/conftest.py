import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contraindications.models import Contraindication, ContraindicationCategory
from reference_books.models import CategoryInfection, Infection, Ingredients

User = get_user_model()


@pytest.fixture
def api_client():
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def sample_infections(db):
    """Создает инфекции и их категории для pytest-тестов."""
    category1 = CategoryInfection.objects.create(name='virusnye')
    category2 = CategoryInfection.objects.create(name='bakterialnye')

    infections = [
        Infection.objects.create(name='Гепатит B', category=category1),
        Infection.objects.create(name='Туберкулез', category=category2),
        Infection.objects.create(name='Корь', category=category1),
        Infection.objects.create(name='Дифтерия', category=category2),
    ]
    return infections


@pytest.fixture
def sample_categories(db):
    """Создает категории противопоказаний для pytest-тестов."""
    category1 = ContraindicationCategory.objects.create(name='Абсолютные')
    category2 = ContraindicationCategory.objects.create(name='Относительные')
    return [category1, category2]


@pytest.fixture
def sample_contraindications(db, sample_categories):
    """Создает противопоказания с привязкой к категориям для pytest-тестов."""
    category1, category2 = sample_categories

    contraindication1 = Contraindication.objects.create(name='Аллергия на компоненты')
    contraindication1.categories.add(category1)

    contraindication2 = Contraindication.objects.create(name='Беременность')
    contraindication2.categories.add(category2)

    return [contraindication1, contraindication2]


@pytest.fixture
def sample_ingredients(db):
    """Создает ингредиенты для pytest-тестов."""
    ingredients = [
        Ingredients.objects.create(name='Алюминия гидроксид', type='Вспомогательное вещество'),
        Ingredients.objects.create(name='Анатоксин дифтерийный', type='Действующее вещество'),
        Ingredients.objects.create(name='Анатоксин столбнячный', type='Действующее вещество'),
    ]
    return ingredients
