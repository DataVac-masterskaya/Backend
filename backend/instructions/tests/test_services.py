from decimal import Decimal

import pytest

from instructions.models import OfficialInstruction
from instructions.services import (
    get_vaccines_by_official_instruction,
    increment_official_instruction_select_count,
    search_official_instructions,
)
from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db


def test_get_vaccines_by_official_instruction_returns_published_visible_vaccines(test_user):
    """Проверяет получение опубликованных видимых вакцин по официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )
    vaccine_card = VaccineCard.objects.create(is_visible=True)
    version = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card,
        name='Пентаксим',
        official_name='Пентаксим вакцина',
        manufacturer='Sanofi',
        official_instruction=instruction,
        created_by=test_user,
    )
    vaccine_card.published_version = version
    vaccine_card.save(update_fields=['published_version'])

    assert get_vaccines_by_official_instruction(instruction.id) == [
        {
            'id': vaccine_card.id,
            'name': 'Пентаксим',
            'officialName': 'Пентаксим вакцина',
            'manufacturer': 'Sanofi',
        },
    ]


def test_get_vaccines_by_official_instruction_ignores_hidden_and_unpublished_vaccines(test_user):
    """Проверяет, что скрытые и неопубликованные вакцины не попадают в список."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )
    hidden_card = VaccineCard.objects.create(is_visible=False)
    hidden_version = VaccineCardVersion.objects.create(
        vaccine_card=hidden_card,
        name='Скрытая вакцина',
        official_instruction=instruction,
        created_by=test_user,
    )
    hidden_card.published_version = hidden_version
    hidden_card.save(update_fields=['published_version'])
    draft_card = VaccineCard.objects.create(is_visible=True)
    VaccineCardVersion.objects.create(
        vaccine_card=draft_card,
        name='Черновик',
        official_instruction=instruction,
        created_by=test_user,
    )

    assert get_vaccines_by_official_instruction(instruction.id) == []


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
