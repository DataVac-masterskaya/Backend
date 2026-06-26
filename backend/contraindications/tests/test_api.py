import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from contraindications.models import Contraindication, ContraindicationCategory
from vaccines.models import (
    VaccineCard,
    VaccineCardVersion,
    VaccineCardVersionContraindication,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def user():
    """Создает пользователя для обязательных связей версий вакцин."""
    return get_user_model().objects.create_user(username='author')


def create_vaccine_for_contraindication(
    user,
    contraindication: Contraindication,
) -> VaccineCard:
    """Создает видимую вакцину, связанную с противопоказанием."""
    vaccine_card = VaccineCard.objects.create(is_visible=True)
    version = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card,
        name='Вакцина АДС-М',
        official_name='Анатоксин дифтерийно-столбнячный',
        created_by=user,
    )
    vaccine_card.published_version = version
    vaccine_card.save(update_fields=('published_version',))
    VaccineCardVersionContraindication.objects.create(
        vaccine_card_version=version,
        contraindication=contraindication,
    )
    return vaccine_card


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


def test_vaccines_endpoint_returns_related_vaccines(
    api_client: APIClient,
    user,
):
    """Проверяет список вакцин по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = create_vaccine_for_contraindication(user, contraindication)

    response = api_client.get(
        f'/api/v1/contraindications/{contraindication.id}/vaccines/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contraindicationId'] == contraindication.id
    assert response.data['vaccines'][0]['id'] == vaccine_card.id
    assert response.data['vaccines'][0]['name'] == 'Вакцина АДС-М'
    assert response.data['vaccines'][0]['contraindications'][0]['name'] == 'Аллергия'


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
