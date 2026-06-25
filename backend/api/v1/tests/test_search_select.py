import pytest
from contraindications.models import Contraindication
from instructions.models import OfficialInstruction
from reference_books.models import CategoryInfection, Infection, Ingredients
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def infection(db):
    """Создает тестовую инфекцию."""
    category = CategoryInfection.objects.create(name='test')
    return Infection.objects.create(name='Грипп', category=category)


@pytest.fixture
def ingredient(db):
    """Создает тестовый ингредиент."""
    return Ingredients.objects.create(name='Алюминия гидроксид', type='адъювант')


@pytest.fixture
def contraindication(db):
    """Создает тестовое противопоказание."""
    return Contraindication.objects.create(name='Аллергия')


@pytest.fixture
def instruction(db):
    """Создает тестовую официальную инструкцию."""
    return OfficialInstruction.objects.create(
        title='Инструкция к вакцине',
        url='https://example.com/instruction',
    )


def test_select_infection_increments_counter(api_client, infection):
    """Проверяет увеличение счётчика для инфекции."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'infection', 'entityId': infection.id},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'success': True}
    infection.refresh_from_db()
    assert infection.search_select_count == 1


def test_select_ingredient_increments_counter(api_client, ingredient):
    """Проверяет увеличение счётчика для ингредиента."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'ingredient', 'entityId': ingredient.id},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'success': True}
    ingredient.refresh_from_db()
    assert ingredient.search_select_count == 1


def test_select_contraindication_increments_counter(api_client, contraindication):
    """Проверяет увеличение счётчика для противопоказания."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'contraindication', 'entityId': contraindication.id},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'success': True}
    contraindication.refresh_from_db()
    assert contraindication.search_select_count == 1


def test_select_instruction_increments_counter(api_client, instruction):
    """Проверяет увеличение счётчика для официальной инструкции."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'instruction', 'entityId': instruction.id},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'success': True}
    instruction.refresh_from_db()
    assert instruction.search_select_count == 1


def test_select_invalid_entity_type_returns_400(api_client):
    """Проверяет ошибку 400 при неверном entityType."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'unknown', 'entityId': 1},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_select_nonexistent_entity_returns_404(api_client):
    """Проверяет ошибку 404 при несуществующем entityId."""
    response = api_client.post(
        '/api/v1/search/select',
        {'entityType': 'infection', 'entityId': 99999},
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_select_missing_fields_returns_400(api_client):
    """Проверяет ошибку 400 при отсутствии обязательных полей."""
    response = api_client.post(
        '/api/v1/search/select',
        {},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
