import pytest
from rest_framework import status

from contraindications.models import Contraindication, ContraindicationCategory

pytestmark = pytest.mark.django_db


def test_list_categories(api_client):
    """Проверяет получение категорий в алфавитном порядке."""
    ContraindicationCategory.objects.create(name='Иммунодефициты')
    ContraindicationCategory.objects.create(name='Аллергии')

    response = api_client.get('/api/v1/contraindications/categories/')

    assert response.status_code == status.HTTP_200_OK
    assert [item['name'] for item in response.data] == [
        'Аллергии',
        'Иммунодефициты',
    ]


def test_list_contraindications(api_client):
    """Проверяет новый формат списка противопоказаний."""
    category = ContraindicationCategory.objects.create(name='Аллергии')
    contraindication = Contraindication.objects.create(
        name='Аллергия на компонент вакцины',
        subcategory='Аллергия на лекарственные компоненты',
        search_select_count=12,
    )
    contraindication.categories.add(category)

    response = api_client.get('/api/v1/contraindications/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            'id': contraindication.id,
            'name': 'Аллергия на компонент вакцины',
            'category': {
                'id': category.id,
                'name': 'Аллергии',
            },
            'subcategory': 'Аллергия на лекарственные компоненты',
            'popularity': 12,
        },
    ]


def test_new_list_uses_first_category_alphabetically(api_client):
    """Проверяет выбор первой категории для нового контракта."""
    allergies = ContraindicationCategory.objects.create(name='Аллергии')
    chronic = ContraindicationCategory.objects.create(name='Хронические заболевания')
    contraindication = Contraindication.objects.create(name='Бронхиальная астма')
    contraindication.categories.add(chronic, allergies)

    response = api_client.get('/api/v1/contraindications/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['category']['name'] == 'Аллергии'


def test_new_list_returns_null_category_and_subcategory(api_client):
    """Проверяет nullable-поля нового контракта."""
    Contraindication.objects.create(name='Противопоказание без категории')

    response = api_client.get('/api/v1/contraindications/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['category'] is None
    assert response.data[0]['subcategory'] is None


def test_new_list_filters_by_category_name(api_client):
    """Проверяет фильтрацию нового списка по названию категории."""
    allergies = ContraindicationCategory.objects.create(name='Аллергии')
    immune = ContraindicationCategory.objects.create(name='Иммунодефициты')
    first = Contraindication.objects.create(name='Аллергия')
    second = Contraindication.objects.create(name='Иммунодефицит')
    first.categories.add(allergies)
    second.categories.add(immune)

    response = api_client.get('/api/v1/contraindications/?category=Аллергии')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия'


def test_new_list_sorts_by_popularity(api_client):
    """Проверяет сортировку по убыванию популярности."""
    Contraindication.objects.create(name='Менее популярное', search_select_count=2)
    Contraindication.objects.create(name='Популярное Б', search_select_count=10)
    Contraindication.objects.create(name='Популярное А', search_select_count=10)

    response = api_client.get('/api/v1/contraindications/?sort=popularity')

    assert response.status_code == status.HTTP_200_OK
    assert [item['name'] for item in response.data] == [
        'Популярное А',
        'Популярное Б',
        'Менее популярное',
    ]


def test_new_list_rejects_invalid_sort(api_client):
    """Проверяет ошибку для неподдерживаемой сортировки."""
    response = api_client.get('/api/v1/contraindications/?sort=unknown')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'detail': 'sort must be one of: popularity, name.',
    }


def test_legacy_list_preserves_old_contract(api_client):
    """Проверяет сохранение прежнего формата на legacy-маршруте."""
    category = ContraindicationCategory.objects.create(name='Аллергии')
    contraindication = Contraindication.objects.create(
        name='Аллергия',
        search_select_count=3,
        search_weight='4.00',
    )
    contraindication.categories.add(category)

    response = api_client.get('/api/v1/contraindications/legacy/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
        {
            'id': contraindication.id,
            'name': 'Аллергия',
            'categories': [{'id': category.id, 'name': 'Аллергии'}],
            'searchSelectCount': 3,
            'searchWeight': '4.00',
        },
    ]


def test_legacy_list_filters_by_category_id(api_client):
    """Проверяет старую фильтрацию по идентификатору категории."""
    allergies = ContraindicationCategory.objects.create(name='Аллергии')
    immune = ContraindicationCategory.objects.create(name='Иммунодефициты')
    first = Contraindication.objects.create(name='Аллергия')
    second = Contraindication.objects.create(name='Иммунодефицит')
    first.categories.add(allergies)
    second.categories.add(immune)

    response = api_client.get(
        f'/api/v1/contraindications/legacy/?categoryId={allergies.id}',
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия'


def test_legacy_list_rejects_invalid_category_id(api_client):
    """Проверяет старую валидацию идентификатора категории."""
    response = api_client.get('/api/v1/contraindications/legacy/?categoryId=abc')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_legacy_list_searches_by_name(api_client):
    """Проверяет старый поиск по названию."""
    Contraindication.objects.create(name='Аллергия')
    Contraindication.objects.create(name='Иммунодефицит')

    response = api_client.get('/api/v1/contraindications/legacy/?search=Аллер')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Аллергия'


def test_detail_contraindication(api_client):
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


def test_detail_contraindication_returns_404(api_client):
    """Проверяет ответ 404 для отсутствующего противопоказания."""
    response = api_client.get('/api/v1/contraindications/999/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    'invalid_id',
    ('-1', '0', 'abc', '1abc', '1.5', '1%20'),
)
def test_detail_contraindication_rejects_invalid_id(api_client, invalid_id):
    """Проверяет ответ 400 для некорректного ID в detail endpoint."""
    response = api_client.get(
        f'/api/v1/contraindications/{invalid_id}/',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'id' in response.data


def test_vaccines_endpoint_returns_related_vaccines(
    api_client,
    vaccine_with_contraindication,
    contraindication_vaccines_url,
):
    """Проверяет список вакцин по противопоказанию."""
    contraindication = vaccine_with_contraindication['contraindication']
    vaccine_card = vaccine_with_contraindication['vaccine_card']

    response = api_client.get(
        contraindication_vaccines_url(contraindication.id),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contraindicationId'] == contraindication.id
    assert response.data['vaccines'][0]['id'] == vaccine_card.id
    assert response.data['vaccines'][0]['name'] == 'Вакцина АДС-М'
    assert response.data['vaccines'][0]['contraindications'][0]['name'] == 'Аллергия'


def test_search_endpoint(api_client):
    """Проверяет отдельный endpoint поисковых подсказок."""
    Contraindication.objects.create(name='Аллергия')

    response = api_client.get('/api/v1/contraindications/search/?q=Аллер')

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == 'Аллергия'


@pytest.mark.parametrize(
    'url',
    (
        '/api/v1/contraindications/search/',
        '/api/v1/contraindications/search/?q=',
        '/api/v1/contraindications/search/?q=%20%20',
    ),
)
def test_search_endpoint_rejects_empty_query(api_client, url):
    """Проверяет обязательность непустого поискового запроса."""
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'q' in response.data


def test_search_endpoint_rejects_too_long_query(api_client):
    """Проверяет ограничение поискового запроса в 255 символов."""
    response = api_client.get(
        '/api/v1/contraindications/search/',
        {'q': 'A' * 256},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'q' in response.data


def test_search_endpoint_allows_query_at_max_length(api_client):
    """Проверяет допустимый запрос длиной ровно 255 символов."""
    response = api_client.get(
        '/api/v1/contraindications/search/',
        {'q': 'A' * 255},
    )

    assert response.status_code == status.HTTP_200_OK


def test_search_endpoint_rejects_only_special_characters(api_client):
    """Проверяет запрет запроса только из специальных символов."""
    response = api_client.get(
        '/api/v1/contraindications/search/',
        {'q': '!@#$'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'q' in response.data


@pytest.mark.parametrize(
    'query',
    (
        'COVID-19',
        'ОРВИ 38°C',
        'Аллергия (острая форма)',
    ),
)
def test_search_endpoint_allows_medical_punctuation(api_client, query):
    """Проверяет допустимую пунктуацию в медицинских запросах."""
    response = api_client.get(
        '/api/v1/contraindications/search/',
        {'q': query},
    )

    assert response.status_code == status.HTTP_200_OK


def test_select_endpoint_increments_select_count(api_client):
    """Проверяет увеличение счетчика выбора подсказки."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    response = api_client.post(
        f'/api/v1/contraindications/{contraindication.id}/select/',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1


@pytest.mark.parametrize(
    'invalid_id',
    ('-1', '0', 'abc', '1abc', '1.5', '1%20'),
)
def test_select_endpoint_rejects_invalid_id(api_client, invalid_id):
    """Проверяет ответ 400 для некорректного ID в select endpoint."""
    response = api_client.post(
        f'/api/v1/contraindications/{invalid_id}/select/',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'id' in response.data


def test_select_endpoint_returns_404_for_missing_id(api_client):
    """Проверяет ответ 404 для корректного отсутствующего ID."""
    response = api_client.post(
        '/api/v1/contraindications/999/select/',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
