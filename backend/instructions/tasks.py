import logging

from celery import shared_task

from instructions.models import OfficialInstruction
from instructions.parsing import check_official_instruction_update

logger = logging.getLogger(__name__)


@shared_task
def check_official_instructions_updates() -> None:
    """Раз в неделю сверяет сохранённые инструкции с источником (ГРЛС/ОХЛП).

    При обнаружении изменения текста выставляет OfficialInstruction.has_update.
    """
    instructions = OfficialInstruction.objects.exclude(url='')
    for instruction in instructions:
        check_official_instruction_update(instruction)
