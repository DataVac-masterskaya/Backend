import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from instructions.admin import OfficialInstructionAdmin
from instructions.models import OfficialInstruction

pytestmark = pytest.mark.django_db


def test_mark_as_reviewed_action_clears_flag():
    """Действие «Отметить как просмотренное» сбрасывает has_update у выбранных строк."""
    instruction = OfficialInstruction.objects.create(
        title='Пентаксим', url='https://grls.rosminzdrav.ru/pentaxim', has_update=True
    )
    admin = OfficialInstructionAdmin(OfficialInstruction, admin_site=None)
    request = RequestFactory().post('/admin/instructions/officialinstruction/')
    request.session = {}
    request._messages = FallbackStorage(request)

    admin.mark_as_reviewed(request, OfficialInstruction.objects.filter(id=instruction.id))

    instruction.refresh_from_db()
    assert instruction.has_update is False
