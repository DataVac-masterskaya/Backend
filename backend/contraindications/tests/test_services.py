from decimal import Decimal

import pytest

from contraindications.models import Contraindication
from contraindications.services import (
    get_vaccines_by_contraindication,
    increment_contraindication_select_count,
    search_contraindications,
)

pytestmark = pytest.mark.django_db


def test_vaccines_stub_returns_empty_list():
    """Проверяет, что заглушка вакцин возвращает пустой список."""
    assert get_vaccines_by_contraindication(1) == []


def test_increment_select_count():
    """Проверяет увеличение счетчика выбора противопоказания."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    increment_contraindication_select_count(contraindication.id)

    contraindication.refresh_from_db()
    assert contraindication.search_select_count == 1


def test_search_limits_results_to_six():
    """Проверяет ограничение поисковой выдачи шестью результатами."""
    for index in range(7):
        Contraindication.objects.create(name=f'Аллергия {index}')

    results = list(search_contraindications('Аллергия'))

    assert len(results) == 6


def test_search_orders_by_score_then_name():
    """Проверяет сортировку поиска по весу и названию."""
    Contraindication.objects.create(
        name='Бета',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    Contraindication.objects.create(
        name='Альфа',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    Contraindication.objects.create(
        name='Гамма',
        search_weight=Decimal('5.00'),
        search_select_count=0,
    )

    results = list(search_contraindications(''))

    assert [item.name for item in results] == ['Гамма', 'Альфа', 'Бета']
