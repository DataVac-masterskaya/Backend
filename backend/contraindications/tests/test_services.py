from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from contraindications.models import Contraindication
from contraindications.services import (
    get_vaccines_by_contraindication,
    increment_contraindication_select_count,
    search_contraindications,
)
from reference_books.models import MethodsOfAdministration
from vaccines.models import (
    VaccineCard,
    VaccineCardVersion,
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    """Создает пользователя для обязательных связей версий вакцин."""
    return get_user_model().objects.create_user(username='author')


def create_published_vaccine(user, name: str = 'Вакцина АДС-М') -> VaccineCard:
    """Создает опубликованную видимую карточку вакцины."""
    vaccine_card = VaccineCard.objects.create(is_visible=True)
    version = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card,
        name=name,
        official_name='Анатоксин дифтерийно-столбнячный',
        min_age='6 лет',
        max_age='без ограничений',
        pregnancy_usage_status='caution',
        created_by=user,
    )
    vaccine_card.published_version = version
    vaccine_card.save(update_fields=('published_version',))
    return vaccine_card


def test_get_vaccines_by_contraindication_returns_related_vaccines(user):
    """Проверяет получение видимых опубликованных вакцин по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = create_published_vaccine(user)
    method = MethodsOfAdministration.objects.create(
        name='Внутримышечно',
        list_icon_url='list.png',
        detail_image_url='detail.png',
    )
    VaccineCardVersionContraindication.objects.create(
        vaccine_card_version=vaccine_card.published_version,
        contraindication=contraindication,
    )
    VaccineCardVersionAdministrationMethod.objects.create(
        vaccine_card_version=vaccine_card.published_version,
        administration_method=method,
        age_group='дети',
        note='по инструкции',
    )

    vaccines = get_vaccines_by_contraindication(contraindication.id)

    assert vaccines == [
        {
            'id': vaccine_card.id,
            'name': 'Вакцина АДС-М',
            'officialName': 'Анатоксин дифтерийно-столбнячный',
            'minAge': '6 лет',
            'maxAge': 'без ограничений',
            'pregnancyUsageStatus': 'caution',
            'contraindications': [
                {
                    'id': contraindication.id,
                    'name': 'Аллергия',
                    'type': 'absolute',
                },
            ],
            'administrationMethods': [
                {
                    'id': method.id,
                    'name': 'Внутримышечно',
                    'ageGroup': 'дети',
                    'note': 'по инструкции',
                },
            ],
        },
    ]


def test_get_vaccines_by_contraindication_excludes_hidden_vaccines(user):
    """Проверяет, что скрытые вакцины не попадают в список по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = create_published_vaccine(user)
    vaccine_card.is_visible = False
    vaccine_card.save(update_fields=('is_visible',))
    VaccineCardVersionContraindication.objects.create(
        vaccine_card_version=vaccine_card.published_version,
        contraindication=contraindication,
    )

    assert get_vaccines_by_contraindication(contraindication.id) == []


def test_increment_select_count():
    """Проверяет увеличение счетчика выбора противопоказания."""
    contraindication = Contraindication.objects.create(name='Аллергия')

    increment_contraindication_select_count(contraindication.id)

    contraindication.refresh_from_db()
    assert contraindication.search_select_count == 1


def test_search_limits_results_to_six():
    """Проверяет ограничение поисковой выдачи шестью результатами."""
    for index in range(7):
        Contraindication.objects.create(name=f'Аллергия {index}')

    results = list(search_contraindications('Аллергия'))

    assert len(results) == 6


def test_search_orders_by_score_then_name():
    """Проверяет сортировку поиска по весу и названию."""
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

    results = list(search_contraindications(''))

    assert [item.name for item in results] == ['Гамма', 'Альфа', 'Бета']
