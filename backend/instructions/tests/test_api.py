import pytest
from rest_framework import status
from rest_framework.test import APIClient

from instructions.models import OfficialInstruction
from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db

OFFICIAL_INSTRUCTION_TITLE = 'Инструкция Пентаксим'
OFFICIAL_INSTRUCTION_URL = 'https://grls.rosminzdrav.ru/instruction/pentaxim'


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def official_instruction():
    """Создает тестовую официальную инструкцию."""
    return OfficialInstruction.objects.create(
        title=OFFICIAL_INSTRUCTION_TITLE,
        url=OFFICIAL_INSTRUCTION_URL,
    )


@pytest.fixture
def published_instruction_vaccine(official_instruction, test_user):
    """Создает опубликованную вакцину, связанную с официальной инструкцией."""
    vaccine_card = VaccineCard.objects.create(is_visible=True)
    version = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card,
        name='Пентаксим',
        official_name='Пентаксим вакцина',
        manufacturer='Sanofi',
        official_instruction=official_instruction,
        created_by=test_user,
    )
    vaccine_card.published_version = version
    vaccine_card.save(update_fields=['published_version'])
    return vaccine_card


def test_list_official_instructions(api_client: APIClient, official_instruction):
    """Проверяет получение списка официальных инструкций."""
    response = api_client.get('/api/v1/instructions/official/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == official_instruction.title
    assert response.data[0]['source'] == 'ГРЛС'


def test_filter_official_instructions_by_source(api_client: APIClient):
    """Проверяет фильтрацию официальных инструкций по источнику."""
    OfficialInstruction.objects.create(
        title='Инструкция из ГРЛС',
        url='https://grls.rosminzdrav.ru/instruction/one',
        source='ГРЛС',
    )
    OfficialInstruction.objects.create(
        title='Инструкция из другого источника',
        url='https://example.com/instruction/two',
        source='Другой источник',
    )

    response = api_client.get('/api/v1/instructions/official/?source=ГРЛС')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Инструкция из ГРЛС'


def test_search_official_instructions_by_title(api_client: APIClient, official_instruction):
    """Проверяет поиск официальных инструкций по названию."""
    OfficialInstruction.objects.create(
        title='Инструкция Инфанрикс',
        url='https://grls.rosminzdrav.ru/instruction/infanrix',
    )

    response = api_client.get('/api/v1/instructions/official/?search=пента')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == official_instruction.title


def test_detail_official_instruction(
    api_client: APIClient,
    official_instruction,
    published_instruction_vaccine,
):
    """Проверяет получение детальной информации об официальной инструкции."""
    response = api_client.get(
        f'/api/v1/instructions/official/{official_instruction.id}/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == OFFICIAL_INSTRUCTION_TITLE
    assert len(response.data['vaccines']) == 1
    vaccine = response.data['vaccines'][0]
    assert vaccine['id'] == published_instruction_vaccine.id
    assert vaccine['name'] == 'Пентаксим'
    assert vaccine['officialName'] == 'Пентаксим вакцина'
    assert vaccine['manufacturer'] == 'Sanofi'


def test_detail_official_instruction_returns_404(api_client: APIClient):
    """Проверяет ответ 404 для отсутствующей официальной инструкции."""
    response = api_client.get('/api/v1/instructions/official/999/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_vaccines_endpoint_returns_related_vaccines(
    api_client: APIClient,
    official_instruction,
    published_instruction_vaccine,
):
    """Проверяет список вакцин по официальной инструкции."""
    response = api_client.get(
        f'/api/v1/instructions/official/{official_instruction.id}/vaccines/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['instructionId'] == official_instruction.id
    assert len(response.data['vaccines']) == 1
    vaccine = response.data['vaccines'][0]
    assert vaccine['id'] == published_instruction_vaccine.id
    assert vaccine['name'] == 'Пентаксим'
    assert vaccine['officialName'] == 'Пентаксим вакцина'
    assert vaccine['manufacturer'] == 'Sanofi'


def test_search_endpoint(api_client: APIClient, official_instruction):
    """Проверяет отдельный endpoint поисковых подсказок."""
    response = api_client.get('/api/v1/instructions/official/search/?q=пента')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['title'] == official_instruction.title


def test_select_endpoint_increments_select_count(api_client: APIClient, official_instruction):
    """Проверяет увеличение счетчика выбора подсказки."""
    response = api_client.post(
        f'/api/v1/instructions/official/{official_instruction.id}/select/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
