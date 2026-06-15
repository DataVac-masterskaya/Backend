import pytest
from rest_framework import status
from rest_framework.test import APIClient

from instructions.models import OfficialInstruction

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


def test_list_official_instructions(api_client: APIClient):
    """Проверяет получение списка официальных инструкций."""
    OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.get('/api/v1/instructions/official/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Инструкция Пентаксим'
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


def test_search_official_instructions_by_title(api_client: APIClient):
    """Проверяет поиск официальных инструкций по названию."""
    OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )
    OfficialInstruction.objects.create(
        title='Инструкция Инфанрикс',
        url='https://grls.rosminzdrav.ru/instruction/infanrix',
    )

    response = api_client.get('/api/v1/instructions/official/?search=пента')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Инструкция Пентаксим'


def test_detail_official_instruction(api_client: APIClient):
    """Проверяет получение детальной информации об официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.get(
        f'/api/v1/instructions/official/{instruction.id}/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Инструкция Пентаксим'
    assert response.data['vaccines'] == []


def test_detail_official_instruction_returns_404(api_client: APIClient):
    """Проверяет ответ 404 для отсутствующей официальной инструкции."""
    response = api_client.get('/api/v1/instructions/official/999/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_vaccines_endpoint_returns_stub(api_client: APIClient):
    """Проверяет заглушку списка вакцин по официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.get(
        f'/api/v1/instructions/official/{instruction.id}/vaccines/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['instructionId'] == instruction.id
    assert response.data['vaccines'] == []


def test_search_endpoint(api_client: APIClient):
    """Проверяет отдельный endpoint поисковых подсказок."""
    OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.get('/api/v1/instructions/official/search/?q=пента')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['title'] == 'Инструкция Пентаксим'


def test_select_endpoint_increments_select_count(api_client: APIClient):
    """Проверяет увеличение счетчика выбора подсказки."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.post(
        f'/api/v1/instructions/official/{instruction.id}/select/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
