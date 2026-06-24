from decimal import Decimal

import pytest

from reference_books.models import (
    CategoryInfection, Infection, MethodsOfAdministration
)

pytestmark = pytest.mark.django_db


def test_create_category_infection():
    """Проверяет создание категории инфекции."""
    category = CategoryInfection.objects.create(name='категория')

    assert str(category) == 'категория'


def test_create_infection():
    """Проверяет создание инфекции."""
    category = CategoryInfection.objects.create(name='категория')
    infection = Infection.objects.create(
        name='инфекция',
        category=category,
    )

    assert str(infection) == 'инфекция'
    assert infection.search_select_count == 0
    assert infection.search_weight == 0


def test_create_methods_of_administration():
    """Проверяет создание способа введения."""
    methods_of_administration = MethodsOfAdministration.objects.create(
        name='способа введения',
        description='Описание способа введения'
    )

    assert str(methods_of_administration) == 'способа введения'
    assert methods_of_administration.description == 'Описание способа введения'
