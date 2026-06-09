from decimal import Decimal

import pytest

from contraindications.models import Contraindication, ContraindicationCategory

pytestmark = pytest.mark.django_db


def test_create_category():
    """Проверяет создание категории противопоказаний."""
    category = ContraindicationCategory.objects.create(name='Аллергии')

    assert str(category) == 'Аллергии'


def test_create_contraindication_with_defaults():
    """Проверяет создание противопоказания со значениями по умолчанию."""
    contraindication = Contraindication.objects.create(
        name='Аллергия на компонент вакцины',
    )

    assert str(contraindication) == 'Аллергия на компонент вакцины'
    assert contraindication.search_select_count == 0
    assert contraindication.search_weight == Decimal('0')


def test_add_single_category_to_contraindication():
    """Проверяет связь противопоказания с одной категорией."""
    category = ContraindicationCategory.objects.create(name='Аллергии')
    contraindication = Contraindication.objects.create(
        name='Аллергия на компонент вакцины',
    )

    contraindication.categories.add(category)

    assert category in contraindication.categories.all()


def test_add_multiple_categories_to_contraindication():
    """Проверяет связь противопоказания с несколькими категориями."""
    allergies = ContraindicationCategory.objects.create(name='Аллергии')
    hypersensitivity = ContraindicationCategory.objects.create(
        name='Гиперчувствительность',
    )
    contraindication = Contraindication.objects.create(
        name='Тяжелая реакция на предыдущую дозу',
    )

    contraindication.categories.add(allergies, hypersensitivity)

    assert contraindication.categories.count() == 2
