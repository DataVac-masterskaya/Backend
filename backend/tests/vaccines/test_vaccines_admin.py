import pytest
from rest_framework import status

from instructions.models import OfficialInstruction
from vaccines.models import VaccineCardStatus, VaccineCardVersion


@pytest.mark.django_db
def test_create_vaccine_success(auth_client, minimal_vaccine_payload, admin_vaccines_card_url):
    """Тест успешного создания карточки вакцины."""
    response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == VaccineCardStatus.DRAFT
    assert 'current_version_id' in response.data


@pytest.mark.django_db
def test_create_vaccine_with_official_instruction(
    auth_client,
    minimal_vaccine_payload,
    admin_vaccines_card_url,
):
    """Проверяет сохранение связи версии вакцины с официальной инструкцией."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )
    minimal_vaccine_payload['official_instruction_id'] = instruction.id

    response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')

    version = VaccineCardVersion.objects.get(id=response.data['current_version_id'])
    assert response.status_code == status.HTTP_201_CREATED
    assert version.official_instruction == instruction
