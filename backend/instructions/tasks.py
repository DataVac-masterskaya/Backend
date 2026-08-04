import logging

from accounts.models import RoleChoices, User
from celery import shared_task
from notifications.models import Notification

from instructions.models import OfficialInstruction
from instructions.parsing import check_official_instruction_update

logger = logging.getLogger(__name__)


@shared_task
def check_official_instructions_updates() -> None:
    """Раз в неделю сверяет сохранённые инструкции с источником (ГРЛС/ОХЛП).

    При обнаружении изменения текста выставляет OfficialInstruction.has_update
    и создаёт уведомление для админов.
    """
    instructions = OfficialInstruction.objects.exclude(url='')
    for instruction in instructions:
        if check_official_instruction_update(instruction):
            notify_admins_instruction_updated(instruction)


def notify_admins_instruction_updated(instruction: OfficialInstruction) -> None:
    admins = User.objects.filter(role=RoleChoices.ADMIN)
    Notification.objects.bulk_create(
        Notification(
            entity_id=instruction.id,
            type='instruction_source_updated',
            recipient=admin,
            data={'title': instruction.title, 'source': instruction.source, 'url': instruction.url},
        )
        for admin in admins
    )
