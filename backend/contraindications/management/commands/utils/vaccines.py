import re

from django.core.management.base import CommandError

from contraindications.management.commands.utils.common import bool_usage, clean_text, get_sheet, get_version_by_old_id
from vaccines.constants import AGES_MAP
from vaccines.models import VaccineCard, VaccineCardStatus, VaccineCardVersion, VersionStatus


def clean_url(url):
    """Очищает url, заменяет аналоги дефиса на нормальный."""
    if not url:
        return None

    url = url.strip()

    url = re.sub(r'[\s\u00a0]*[–—−][\s\u00a0]*', '-', url)

    return url


def import_vaccines(wb):
    """Импорт карточек и версий вакцин."""
    ws = get_sheet(wb, 'vaccines')
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    id_idx = headers.index('id')
    short_name_idx = headers.index('short_name')
    long_name_idx = headers.index('long_name')
    code_name_idx = headers.index('code_name')
    manufacturer_idx = headers.index('manufacturer')
    in_use_in_Russia_idx = headers.index('in_use_in_Russia')
    OKhLP_specialists_link_idx = headers.index('OKhLP_specialists_link')
    GRLS_instruction_link_idx = headers.index('GRLS_instruction_link')

    count_add = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[id_idx] is None:
            continue
        vaccine_id = row[id_idx]
        if isinstance(vaccine_id, str):
            vaccine_id = vaccine_id.strip()
            if vaccine_id.startswith('='):
                vaccine_id = vaccine_id[1:]
        vaccine_id = int(vaccine_id)
        name = row[short_name_idx]
        official_name = row[long_name_idx]
        code_name = row[code_name_idx]
        manufacturer = row[manufacturer_idx]
        in_use_in_Russia = row[in_use_in_Russia_idx]
        in_use_in_Russia = bool_usage(in_use_in_Russia)
        ohlp_url = row[OKhLP_specialists_link_idx]
        instruction_url = row[GRLS_instruction_link_idx]
        if 'нет' or 'есть' in instruction_url:
            instruction_url = None
        if 'нет' or 'есть' in ohlp_url:
            ohlp_url = None
        card, created = VaccineCard.objects.update_or_create(
            old_id=vaccine_id,
            defaults={
                'status': VaccineCardStatus.ACTIVE,
                'is_visible': True,
                'created_by': None,
                'updated_by': None,
            },
        )
        version, _ = VaccineCardVersion.objects.update_or_create(
            old_id=vaccine_id,
            defaults={
                'vaccine_card': card,
                'version_number': 1,
                'version_status': VersionStatus.APPROVED,
                'moderation_request': None,
                'name': name,
                'official_name': official_name,
                'code_name': code_name,
                'manufacturer': manufacturer,
                'is_available_in_rf': in_use_in_Russia,
                'created_by': None,
                'approved_by': None,
                'ohlp_url': ohlp_url,
                'instruction_url': instruction_url,
            },
        )
        if created:
            count_add += 1
    return count_add


def import_vaccine_storage(wb):
    """Импорт условий хранения вакцин."""
    ws = get_sheet(wb, 'storage_text')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_id')
    storage_idx = headers.index('storage_text_w/o_html')

    updated = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccine_id_idx]
        storage = row[storage_idx]

        if vaccine_id is None:
            raise CommandError('В файле обнаружена строка без vaccine_id.')

        if not storage:
            continue

        version = get_version_by_old_id(int(vaccine_id))

        version.storage_conditions = clean_text(storage)
        version.save(update_fields=['storage_conditions'])

        updated += 1

    return updated


def import_vaccine_pregnancy_use(wb):
    """Импорт использования вакцины при беременности."""
    ws = get_sheet(wb, 'pregnancy_BF_text')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_id')
    pregnancy_idx = headers.index('preg_BF_text_w/o_html')

    updated = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[vaccine_id_idx] is None:
            continue
        vaccine_id = row[vaccine_id_idx]
        pregnancy = row[pregnancy_idx]

        if vaccine_id is None:
            raise CommandError('В файле обнаружена строка без vaccine_id.')

        if not pregnancy:
            continue

        version = get_version_by_old_id(int(vaccine_id))

        version.pregnancy_usage_old = clean_text(pregnancy)
        version.save(update_fields=['pregnancy_usage_old'])

        updated += 1

    return updated


def import_vaccine_interaction(wb):
    """Импорт взаимодействия вакцины с другими лекарствами."""
    ws = get_sheet(wb, 'interaction_text')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_id')
    interaction_idx = headers.index('interaction_text_w/o_html')

    updated = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccine_id_idx]
        interaction = row[interaction_idx]

        if vaccine_id is None:
            raise CommandError('В файле обнаружена строка без vaccine_id.')

        if not interaction:
            continue

        version = get_version_by_old_id(int(vaccine_id))

        version.interaction_info = clean_text(interaction)
        version.save(update_fields=['interaction_info'])

        updated += 1

    return updated


def import_vaccine_simult_administration(wb):
    """Импорт взаимодействия вакцины с другими вакцинами."""
    ws = get_sheet(wb, 'simult_administration_text')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_id')
    interaction_idx = headers.index('simult_admin_text_w/o_html')

    updated = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        vaccine_id = row[vaccine_id_idx]
        interaction = row[interaction_idx]

        if vaccine_id is None:
            raise CommandError('В файле обнаружена строка без vaccine_id.')

        if not interaction:
            continue

        version = get_version_by_old_id(int(vaccine_id))

        version.compatibility_info = clean_text(interaction)
        version.save(update_fields=['compatibility_info'])

        updated += 1

    return updated


def set_vaccine_ages(wb):
    """Импорт возрастов использования вакцины."""
    ws = get_sheet(wb, 'vaccines_ages')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_ID')
    ages_from = headers.index('age_from_value')
    ages_to = headers.index('age_through_value')
    updated = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[vaccine_id_idx] is None:
            continue
        vaccine_id = row[vaccine_id_idx]
        age_from = row[ages_from]
        age_to = row[ages_to]
        age_from = clean_text(age_from)
        age_to = clean_text(age_to)
        age_allowed = f'от {ages_from} до {age_to}'
        age_from = AGES_MAP[age_from]
        age_to = AGES_MAP[age_to]
        if vaccine_id is None:
            raise CommandError('В файле обнаружена строка без vaccine_id.')
        version = get_version_by_old_id(int(vaccine_id))
        version.min_age_days = age_from
        version.max_age_days = age_to
        version.age_allowed = age_allowed
        version.save(update_fields=['min_age_days', 'max_age_days', 'age_allowed'])
        updated += 1
    return updated


def set_vaccine_nonspec_links(wb):
    """Импорт ссылок на вкладыш для неспециалистов."""
    ws = get_sheet(wb, 'ages_text')

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    vaccine_id_idx = headers.index('vaccine_id')
    ages_version_link_idx = headers.index('ages_version_link')
    updated = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[vaccine_id_idx] is None:
            continue
        vaccine_id = row[vaccine_id_idx]
        nonspec_instruction_link = row[ages_version_link_idx]
        if not nonspec_instruction_link or '.pdf' not in nonspec_instruction_link:
            nonspec_instruction_link = None
        nonspec_instruction_link = clean_url(nonspec_instruction_link)
        version = get_version_by_old_id(int(vaccine_id))
        version.nonspec_url = nonspec_instruction_link
        version.save(update_fields=['nonspec_url'])
        updated += 1
    return updated


def set_current_version():
    """Устанавливает актуальную и опубликованную версию карточки."""
    cards = VaccineCard.objects.all()
    versions = VaccineCardVersion.objects.all()
    updated = 0
    for card in cards:
        current_version = versions.get(old_id=card.old_id)
        card.current_version = current_version
        card.published_version = current_version
        card.save(update_fields=['current_version', 'published_version'])
        updated += 1
    return updated
