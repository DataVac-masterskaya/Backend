import pytest
from rest_framework import status
from rest_framework.test import APIClient

from contraindications.models import Contraindication, ContraindicationCategory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


def test_list_categories(api_client: APIClient):
    """Проверяет получение категорий в алфавитном порядке."""
    ContraindicationCategory.objects.create(name='Иммунодефициты')
    ContraindicationCategory.objects.create(name='Аллергии')

    response = api_client.get('/api/v1/contraindications/categories/')

    assert response.status_code == status.HTTP_200_OK
    assert [item['name'] for item in response.data] == [
        'Аллергии',
        'Иммунодефициты',
    ]


def test_list_contraindications(api_client: APIClient):
    """Проверяет получение списка противопоказаний."""
    Contraindication.objects.create(name='Аллергия на компонент вакцины')

    response = api_client.get('/api/v1/contraindications/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия на компонент вакцины'


def test_filter_contraindications_by_category(api_client: APIClient):
    """Проверяет фильтрацию противопоказаний по категории."""
    allergies = ContraindicationCategory.objects.create(name='Аллергии')
    immune = ContraindicationCategory.objects.create(name='Иммунодефициты')
    first = Contraindication.objects.create(name='Аллергия')
    second = Contraindication.objects.create(name='Иммунодефицит')
    first.categories.add(allergies)
    second.categories.add(immune)

    response = api_client.get(
        f'/api/v1/contraindications/?categoryId={allergies.id}',
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия'


def test_filter_contraindications_rejects_invalid_category_id(
    api_client: APIClient,
):
    """Проверяет ошибку при некорректном идентификаторе категории."""
    response = api_client.get('/api/v1/contraindications/?categoryId=abc')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_search_contraindications_by_name(api_client: APIClient):
    """Проверяет поиск противопоказаний по названию."""
    Contraindication.objects.create(name='Аллергия')
    Contraindication.objects.create(name='Иммунодефицит')

    response = api_client.get('/api/v1/contraindications/?search=аллер')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия'


def test_detail_contraindication(api_client: APIClient):
    """Проверяет получение детальной информации о противопоказании."""
    category = ContraindicationCategory.objects.create(name='Аллергии')
    contraindication = Contraindication.objects.create(name='Аллергия')
    contraindication.categories.add(category)

    response = api_client.get(
        f'/api/v1/contraindications/{contraindication.id}/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Аллергия'
    assert response.data['vaccines'] == []


def test_detail_contraindication_returns_404(api_client: APIClient):
    """Проверяет ответ 404 для отсутствующего противопоказания."""
    response = api_client.get('/api/v1/contraindications/999/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_vaccines_endpoint_returns_stub(api_client: APIClient):
    """Проверяет заглушку списка вакцин по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    response = api_client.get(
        f'/api/v1/contraindications/{contraindication.id}/vaccines/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contraindicationId'] == contraindication.id
    assert response.data['vaccines'] == []


def test_search_endpoint(api_client: APIClient):
    """Проверяет отдельный endpoint поисковых подсказок."""
    Contraindication.objects.create(name='Аллергия')

    response = api_client.get('/api/v1/contraindications/search/?q=аллер')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Аллергия'


def test_select_endpoint_increments_select_count(api_client: APIClient):
    """Проверяет увеличение счетчика выбора подсказки."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    response = api_client.post(
        f'/api/v1/contraindications/{contraindication.id}/select/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
