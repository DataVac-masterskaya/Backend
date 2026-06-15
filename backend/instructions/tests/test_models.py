from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from instructions.models import OfficialInstruction

pytestmark = pytest.mark.django_db


def test_create_official_instruction_with_defaults():
    """Проверяет создание официальной инструкции со значениями по умолчанию."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    assert str(instruction) == 'Инструкция Пентаксим'
    assert instruction.source == 'ГРЛС'
    assert instruction.description == ''
    assert instruction.search_select_count == 0
    assert instruction.search_weight == Decimal('0')


def test_official_instruction_validates_url():
    """Проверяет валидацию ссылки официальной инструкции."""
    instruction = OfficialInstruction(
        title='Некорректная инструкция',
        url='not-a-url',
    )

    with pytest.raises(ValidationError):
        instruction.full_clean()
