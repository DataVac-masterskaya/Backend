from decimal import Decimal

import pytest

from instructions.models import OfficialInstruction
from instructions.services import (
    get_vaccines_by_official_instruction,
    increment_official_instruction_select_count,
    search_official_instructions,
)

pytestmark = pytest.mark.django_db


def test_vaccines_stub_returns_empty_list():
    """Проверяет, что заглушка вакцин возвращает пустой список."""
    assert get_vaccines_by_official_instruction(1) == []


def test_increment_select_count():
    """Проверяет увеличение счетчика выбора официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    increment_official_instruction_select_count(instruction.id)

    instruction.refresh_from_db()
    assert instruction.search_select_count == 1


def test_search_limits_results_to_six():
    """Проверяет ограничение поисковой выдачи шестью результатами."""
    for index in range(7):
        OfficialInstruction.objects.create(
            title=f'Инструкция {index}',
            url=f'https://grls.rosminzdrav.ru/instruction/{index}',
        )

    results = list(search_official_instructions('Инструкция'))

    assert len(results) == 6


def test_search_orders_by_score_then_title():
    """Проверяет сортировку поиска по весу и названию."""
    OfficialInstruction.objects.create(
        title='Бета',
        url='https://example.com/beta',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    OfficialInstruction.objects.create(
        title='Альфа',
        url='https://example.com/alpha',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    OfficialInstruction.objects.create(
        title='Гамма',
        url='https://example.com/gamma',
        search_weight=Decimal('5.00'),
        search_select_count=0,
    )

    results = list(search_official_instructions(''))

    assert [item.title for item in results] == ['Гамма', 'Альфа', 'Бета']
