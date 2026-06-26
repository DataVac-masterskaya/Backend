from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from instructions.models import OfficialInstruction
from rest_framework import status
from rest_framework.test import APIClient

from contraindications.models import Contraindication
from reference_books.models import CategoryInfection, Infection, Ingredients
from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def infection_category() -> CategoryInfection:
    """Создает категорию инфекций для тестовых записей."""
    return CategoryInfection.objects.create(name='viral')


@pytest.fixture
def user():
    """Создает пользователя для обязательных связей версий вакцин."""
    return get_user_model().objects.create_user(username='author')


def create_vaccine_card(
    user,
    name: str = 'Вакцина АДС-М',
    official_name: str = 'Анатоксин дифтерийно-столбнячный',
    is_visible: bool = True,
) -> VaccineCard:
    """Создает опубликованную карточку вакцины для тестов поиска."""
    vaccine_card = VaccineCard.objects.create(is_visible=is_visible)
    version = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card,
        name=name,
        official_name=official_name,
        created_by=user,
    )
    vaccine_card.published_version = version
    vaccine_card.save(update_fields=('published_version',))
    return vaccine_card


def test_search_suggestions_returns_groups(
    api_client: APIClient,
    infection_category: CategoryInfection,
    user,
):
    """Проверяет, что глобальный поиск возвращает подсказки по группам."""
    Contraindication.objects.create(name='Аллергия')
    Infection.objects.create(name='Аденовирус', category=infection_category)
    Ingredients.objects.create(name='Алюминия гидроксид', type='адъювант')
    OfficialInstruction.objects.create(
        title='Инструкция АДС-М',
        url='https://example.com/instructions/ads-m',
    )
    create_vaccine_card(user)

    response = api_client.get('/api/search/suggestions/?q=а')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contraindications'][0]['name'] == 'Аллергия'
    assert response.data['infections'][0]['name'] == 'Аденовирус'
    assert response.data['ingredients'][0]['name'] == 'Алюминия гидроксид'
    assert response.data['instructions'][0]['name'] == 'Инструкция АДС-М'
    assert response.data['vaccines'][0]['name'] == 'Вакцина АДС-М'


def test_search_suggestions_limits_each_group_to_six(api_client: APIClient):
    """Проверяет ограничение глобального поиска шестью подсказками в группе."""
    for index in range(7):
        Contraindication.objects.create(name=f'Аллергия {index}')

    response = api_client.get('/api/search/suggestions/?q=аллергия')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['contraindications']) == 6


def test_search_suggestions_orders_by_score_then_name(api_client: APIClient):
    """Проверяет сортировку глобального поиска по score и названию."""
    Contraindication.objects.create(
        name='Бета',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    Contraindication.objects.create(
        name='Альфа',
        search_weight=Decimal('2.00'),
        search_select_count=1,
    )
    Contraindication.objects.create(
        name='Гамма',
        search_weight=Decimal('5.00'),
        search_select_count=0,
    )

    response = api_client.get('/api/search/suggestions/?q=')

    assert response.status_code == status.HTTP_200_OK
    assert [item['name'] for item in response.data['contraindications']] == [
        'Гамма',
        'Альфа',
        'Бета',
    ]


def test_search_suggestions_returns_only_visible_published_vaccines(
    api_client: APIClient,
    user,
):
    """Проверяет, что поиск вакцин не отдает скрытые и неопубликованные карточки."""
    visible_vaccine = create_vaccine_card(user, name='Вакцина АДС-М')
    create_vaccine_card(user, name='Скрытая вакцина АДС-М', is_visible=False)
    unpublished_vaccine = VaccineCard.objects.create(is_visible=True)
    VaccineCardVersion.objects.create(
        vaccine_card=unpublished_vaccine,
        name='Черновик АДС-М',
        created_by=user,
    )

    response = api_client.get('/api/search/suggestions/?q=адс')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['vaccines'] == [
        {
            'id': visible_vaccine.id,
            'name': 'Вакцина АДС-М',
            'score': '0.00',
        },
    ]


def test_search_select_increments_contraindication_count(api_client: APIClient):
    """Проверяет увеличение счетчика выбранного противопоказания."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'contraindication',
            'entityId': contraindication.id,
        },
        format='json',
    )

    contraindication.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
    assert contraindication.search_select_count == 1


def test_search_select_increments_infection_count(
    api_client: APIClient,
    infection_category: CategoryInfection,
):
    """Проверяет увеличение счетчика выбранной инфекции."""
    infection = Infection.objects.create(name='Корь', category=infection_category)

    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'infection',
            'entityId': infection.id,
        },
        format='json',
    )

    infection.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
    assert infection.search_select_count == 1


def test_search_select_increments_ingredient_count(api_client: APIClient):
    """Проверяет увеличение счетчика выбранного ингредиента."""
    ingredient = Ingredients.objects.create(name='Неомицин', type='антибиотик')

    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'ingredient',
            'entityId': ingredient.id,
        },
        format='json',
    )

    ingredient.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
    assert ingredient.search_select_count == 1


def test_search_select_increments_instruction_count(api_client: APIClient):
    """Проверяет увеличение счетчика выбранной официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'instruction',
            'entityId': instruction.id,
        },
        format='json',
    )

    instruction.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
    assert instruction.search_select_count == 1


def test_search_select_increments_vaccine_card_count(
    api_client: APIClient,
    user,
):
    """Проверяет увеличение счетчика выбранной карточки вакцины."""
    vaccine_card = create_vaccine_card(user)

    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'vaccineCard',
            'entityId': vaccine_card.id,
        },
        format='json',
    )

    vaccine_card.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data['searchSelectCount'] == 1
    assert vaccine_card.search_select_count == 1


def test_search_select_rejects_unknown_entity_type(api_client: APIClient):
    """Проверяет ошибку валидации для неизвестного типа сущности."""
    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'unknown',
            'entityId': 1,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_search_select_returns_404_for_missing_entity(api_client: APIClient):
    """Проверяет ответ 404 для отсутствующей выбранной сущности."""
    response = api_client.post(
        '/api/search/select/',
        {
            'entityType': 'contraindication',
            'entityId': 999,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
