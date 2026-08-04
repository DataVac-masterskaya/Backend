import pytest

from instructions.models import OfficialInstruction
from instructions.tasks import check_official_instructions_updates

pytestmark = pytest.mark.django_db


def test_check_official_instructions_updates_calls_check_for_each_instruction(monkeypatch):
    """Задача сверяет с источником каждую инструкцию, у которой заполнен url."""
    with_url = OfficialInstruction.objects.create(title='Пентаксим', url='https://grls.rosminzdrav.ru/pentaxim')
    OfficialInstruction.objects.create(title='Без ссылки', url='')

    checked_ids = []
    monkeypatch.setattr(
        'instructions.tasks.check_official_instruction_update',
        lambda instruction: checked_ids.append(instruction.id) or True,
    )

    check_official_instructions_updates()

    assert checked_ids == [with_url.id]
