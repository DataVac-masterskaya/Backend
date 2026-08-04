import pytest
from accounts.models import RoleChoices
from django.contrib.auth import get_user_model
from notifications.models import Notification

from instructions.models import OfficialInstruction
from instructions.tasks import check_official_instructions_updates

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_check_official_instructions_updates_notifies_admins_on_change(monkeypatch):
    """Если источник изменился, каждый админ получает уведомление instruction_source_updated."""
    instruction = OfficialInstruction.objects.create(title='Пентаксим', url='https://grls.rosminzdrav.ru/pentaxim')
    admin = User.objects.create_user(username='admin_user', password='test123', role=RoleChoices.ADMIN)
    monkeypatch.setattr('instructions.tasks.check_official_instruction_update', lambda instruction: True)

    check_official_instructions_updates()

    notification = Notification.objects.get(type='instruction_source_updated')
    assert notification.recipient_id == admin.id
    assert notification.entity_id == instruction.id
