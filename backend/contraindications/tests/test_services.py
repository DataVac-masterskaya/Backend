from decimal import Decimal

import pytest

from contraindications.models import Contraindication
from contraindications.services import (
    get_vaccines_by_contraindication,
    increment_contraindication_select_count,
    search_contraindications,
)
from reference_books.models import MethodsOfAdministration
from vaccines.models import (
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
)

pytestmark = pytest.mark.django_db


def test_get_vaccines_by_contraindication_returns_related_vaccines(published_vaccine_factory):
    """Проверяет получение видимых опубликованных вакцин по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = published_vaccine_factory()
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
            'minAge': 6,
            'maxAge': 18,
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


def test_get_vaccines_by_contraindication_excludes_hidden_vaccines(published_vaccine_factory):
    """Проверяет, что скрытые вакцины не попадают в список по противопоказанию."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = published_vaccine_factory()
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
