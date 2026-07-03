from decimal import Decimal

import pytest
from instructions.models import OfficialInstruction
from rest_framework import status

from contraindications.models import Contraindication
from reference_books.models import Infection, Ingredients
from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db


def test_search_suggestions_returns_groups(
    api_client,
    infection_category,
    published_vaccine_factory,
    search_suggestions_url,
):
    """Проверяет, что глобальный поиск возвращает подсказки по группам."""
    Contraindication.objects.create(name='Аллергия')
    Infection.objects.create(name='Аденовирус', category=infection_category)
    Ingredients.objects.create(name='Алюминия гидроксид', type='адъювант')
    OfficialInstruction.objects.create(
        title='Инструкция АДС-М',
        url='https://example.com/instructions/ads-m',
    )
    published_vaccine_factory()

    response = api_client.get(search_suggestions_url, {'q': 'а'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['contraindications'][0]['name'] == 'Аллергия'
    assert response.data['infections'][0]['name'] == 'Аденовирус'
    assert response.data['ingredients'][0]['name'] == 'Алюминия гидроксид'
    assert response.data['instructions'][0]['name'] == 'Инструкция АДС-М'
    assert response.data['vaccines'][0]['name'] == 'Вакцина АДС-М'


def test_search_suggestions_limits_each_group_to_six(api_client, search_suggestions_url):
    """Проверяет ограничение глобального поиска шестью подсказками в группе."""
    for index in range(7):
        Contraindication.objects.create(name=f'Аллергия {index}')

    response = api_client.get(search_suggestions_url, {'q': 'аллергия'})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['contraindications']) == 6


def test_search_suggestions_orders_by_score_then_name(api_client, search_suggestions_url):
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

    response = api_client.get(search_suggestions_url, {'q': ''})

    assert response.status_code == status.HTTP_200_OK
    assert [item['name'] for item in response.data['contraindications']] == [
        'Гамма',
        'Альфа',
        'Бета',
    ]


def test_search_suggestions_returns_only_visible_published_vaccines(
    api_client,
    published_vaccine_factory,
    test_user,
    search_suggestions_url,
):
    """Проверяет, что поиск вакцин не отдает скрытые и неопубликованные карточки."""
    visible_vaccine = published_vaccine_factory(name='Вакцина АДС-М')
    published_vaccine_factory(name='Скрытая вакцина АДС-М', is_visible=False)
    unpublished_vaccine = VaccineCard.objects.create(is_visible=True)
    VaccineCardVersion.objects.create(
        vaccine_card=unpublished_vaccine,
        name='Черновик АДС-М',
        created_by=test_user,
    )

    response = api_client.get(search_suggestions_url, {'q': 'адс'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['vaccines'] == [
        {
            'id': visible_vaccine.id,
            'name': 'Вакцина АДС-М',
            'score': '0.00',
        },
    ]


def test_search_select_increments_contraindication_count(api_client, search_select_url):
    """Проверяет увеличение счетчика выбранного противопоказания."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    response = api_client.post(
        search_select_url,
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
    api_client,
    infection_category,
    search_select_url,
):
    """Проверяет увеличение счетчика выбранной инфекции."""
    infection = Infection.objects.create(name='Корь', category=infection_category)

    response = api_client.post(
        search_select_url,
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


def test_search_select_increments_ingredient_count(api_client, search_select_url):
    """Проверяет увеличение счетчика выбранного ингредиента."""
    ingredient = Ingredients.objects.create(name='Неомицин', type='антибиотик')

    response = api_client.post(
        search_select_url,
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


def test_search_select_increments_instruction_count(api_client, search_select_url):
    """Проверяет увеличение счетчика выбранной официальной инструкции."""
    instruction = OfficialInstruction.objects.create(
        title='Инструкция Пентаксим',
        url='https://grls.rosminzdrav.ru/instruction/pentaxim',
    )

    response = api_client.post(
        search_select_url,
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
    api_client,
    published_vaccine_factory,
    search_select_url,
):
    """Проверяет увеличение счетчика выбранной карточки вакцины."""
    vaccine_card = published_vaccine_factory()

    response = api_client.post(
        search_select_url,
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


def test_search_select_rejects_unknown_entity_type(api_client, search_select_url):
    """Проверяет ошибку валидации для неизвестного типа сущности."""
    response = api_client.post(
        search_select_url,
        {
            'entityType': 'unknown',
            'entityId': 1,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_search_select_returns_404_for_missing_entity(api_client, search_select_url):
    """Проверяет ответ 404 для отсутствующей выбранной сущности."""
    response = api_client.post(
        search_select_url,
        {
            'entityType': 'contraindication',
            'entityId': 999,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
