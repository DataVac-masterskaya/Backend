from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contraindications.models import Contraindication, ContraindicationCategory
from instructions.models import OfficialInstruction
from reference_books.models import (
    CategoryInfection,
    Infection,
    Ingredients,
    MethodsOfAdministration,
)
from vaccines.models import (
    VaccineCard,
    VaccineCardVersion,
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
    VaccineCardVersionInfection,
    VaccineCardVersionIngredient,
)

User = get_user_model()


@pytest.fixture
def api_client():
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Тестовый пользователь."""
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def sample_categories(db):
    """Создает категории инфекций."""
    category1 = CategoryInfection.objects.create(name='virusnye')
    category2 = CategoryInfection.objects.create(name='bakterialnye')
    return [category1, category2]


@pytest.fixture
def sample_infections(db, sample_categories):
    """Создает тестовые инфекции."""
    category1, category2 = sample_categories

    infections = [
        Infection.objects.create(
            name='Дифтерия',
            category=category1,
            search_weight=10,
            popularity=80,
        ),
        Infection.objects.create(
            name='Столбняк',
            category=category2,
            search_weight=8,
            popularity=70,
        ),
        Infection.objects.create(
            name='Коклюш',
            category=category1,
            search_weight=7,
            popularity=65,
        ),
        Infection.objects.create(
            name='Гепатит B',
            category=category1,
            search_weight=9,
            popularity=75,
        ),
        Infection.objects.create(
            name='Полиомиелит',
            category=category1,
            search_weight=6,
            popularity=60,
        ),
        Infection.objects.create(
            name='Хиб',
            category=category2,
            search_weight=5,
            popularity=55,
        ),
    ]
    return infections


@pytest.fixture
def sample_ingredients(db):
    """Создает тестовые ингредиенты."""
    ingredients = [
        Ingredients.objects.create(
            name='Алюминия гидроксид',
            type='Адъювант',
            search_weight=5,
            popularity=50,
        ),
        Ingredients.objects.create(
            name='Анатоксин дифтерийный',
            type='Стабилизатор',
            search_weight=8,
            popularity=80,
        ),
        Ingredients.objects.create(
            name='Анатоксин столбнячный',
            type='Эмульгатор',
            search_weight=7,
            popularity=70,
        ),
        Ingredients.objects.create(
            name='Формальдегид',
            type='Консервант',
            search_weight=3,
            popularity=30,
        ),
    ]
    return ingredients


@pytest.fixture
def sample_administration_methods(db):
    """Создает методы введения."""
    methods_data = [
        {'name': 'Внутримышечно', 'code': 'intramuscularly'},
        {'name': 'Подкожно', 'code': 'subcutaneously'},
        {'name': 'Накожно', 'code': 'cutaneously'},
        {'name': 'Внутрикожно', 'code': 'intradermally'},
        {'name': 'Капли', 'code': 'drops'},
        {'name': 'Таблетки', 'code': 'pills'},
        {'name': 'Интраназально', 'code': 'intranasally'},
    ]
    methods = []
    for data in methods_data:
        method = MethodsOfAdministration.objects.create(
            name=data['name'],
            code=data['code'],
        )
        methods.append(method)
    return methods


@pytest.fixture
def sample_vaccine_versions(
    db, test_user, sample_infections, sample_ingredients, sample_contraindications, sample_administration_methods
):
    """Создает версии карточек вакцин с полными и минимальными данными."""
    versions = []

    # Вакцина 1: Полная карточка
    vaccine_card_1 = VaccineCard.objects.create(
        status='active',
        is_visible=True,
        search_weight=90,
        popularity=90,
        created_by=test_user,
    )
    version_1 = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card_1,
        version_number=1,
        version_status='approved',
        name='Инфанрикс Гекса',
        official_name='Инфанрикс® Гекса, суспензия для в/м введения',
        is_available_in_rf=False,
        min_age_days=2,
        max_age_days=None,
        pregnancy_usage_status=False,
        revision_date=date(2024, 9, 25),
        nonspec_url='https://grls.rosminzdrav.ru/nonspec-infanrix.pdf',
        instruction_url='https://grls.rosminzdrav.ru/instruction-infanrix.pdf',
        ohlp_url='https://grls.rosminzdrav.ru/infanrix',
        pdf_url='https://grls.rosminzdrav.ru/pdf/infanrix.pdf',
        manufacturer='GlaxoSmithKline',
        storage_conditions='Хранить при температуре от +2°C до +8°C',
        schedule_info='3 дозы с интервалом 1,5 месяца; ревакцинация на 2-м году жизни',
        side_effects='Местные реакции в месте инъекции, субфебрильная температура',
        indications='Активная иммунизация детей от 2 месяцев жизни',
        comment_source='АНО DataVac',
        comment_ANO='В РФ применение при ГВ противопоказано, однако ВОЗ допускает...',
        created_by=test_user,
    )
    for infection in sample_infections:
        VaccineCardVersionInfection.objects.create(
            vaccine_card_version=version_1,
            infection=infection,
        )
    VaccineCardVersionIngredient.objects.create(
        vaccine_card_version=version_1,
        ingredient=sample_ingredients[0],
        role='auxiliary',
    )
    VaccineCardVersionIngredient.objects.create(
        vaccine_card_version=version_1,
        ingredient=sample_ingredients[1],
        role='active',
    )
    VaccineCardVersionContraindication.objects.create(
        vaccine_card_version=version_1,
        contraindication=sample_contraindications[0],
        contraindication_type='absolute',
    )
    VaccineCardVersionAdministrationMethod.objects.create(
        vaccine_card_version=version_1,
        administration_method=sample_administration_methods[0],
    )
    vaccine_card_1.current_version = version_1
    vaccine_card_1.published_version = version_1
    vaccine_card_1.save()
    versions.append(version_1)

    # Вакцина 2: Минимальная карточка
    vaccine_card_2 = VaccineCard.objects.create(
        status='active',
        is_visible=True,
        search_weight=50,
        popularity=50,
        created_by=test_user,
    )
    version_2 = VaccineCardVersion.objects.create(
        vaccine_card=vaccine_card_2,
        version_number=1,
        version_status='approved',
        name='АКДС',
        official_name='Официальное название АКДС',
        pdf_url='https://grls.rosminzdrav.ru/pdf/akds',
        ohlp_url='https://grls.rosminzdrav.ru/akds',
        nonspec_url='https://instructions.ru/patient/akds',
        instruction_url='https://instructions.ru/specialist/akds',
        created_by=test_user,
    )
    vaccine_card_2.current_version = version_2
    vaccine_card_2.published_version = version_2
    vaccine_card_2.save()
    versions.append(version_2)

    return versions


@pytest.fixture
def sample_vaccine_card_with_versions(db, test_user):
    """Создает одну карточку вакцины с несколькими версиями."""
    vaccine_card = VaccineCard.objects.create(
        status='active',
        is_visible=True,
        search_weight=75,
        popularity=75,
        created_by=test_user,
    )

    versions = []
    for i in range(3):
        version = VaccineCardVersion.objects.create(
            vaccine_card=vaccine_card,
            version_number=i + 1,
            version_status='approved' if i == 2 else 'draft',
            name=f'АКДС v{i + 1}',
            official_name=f'Официальное название АКДС v{i + 1}',
            pdf_url=f'https://grls.rosminzdrav.ru/pdf/akds_v{i + 1}',
            ohlp_url=f'https://grls.rosminzdrav.ru/akds_v{i + 1}',
            nonspec_url=f'https://instructions.ru/patient/akds_v{i + 1}',
            instruction_url=f'https://instructions.ru/specialist/akds_v{i + 1}',
            created_by=test_user,
        )
        versions.append(version)

    vaccine_card.current_version = versions[-1]
    vaccine_card.published_version = versions[-1]
    vaccine_card.save()

    return vaccine_card, versions


@pytest.fixture
def sample_contraindication_categories(db):
    """Создает категории противопоказаний."""
    categories = [
        ContraindicationCategory.objects.create(name='Хронические заболевания'),
        ContraindicationCategory.objects.create(name='Аллергические реакции'),
        ContraindicationCategory.objects.create(name='Иммунодефицитные состояния'),
        ContraindicationCategory.objects.create(name='Беременность и лактация'),
        ContraindicationCategory.objects.create(name='Острые заболевания'),
    ]
    return categories


@pytest.fixture
def sample_contraindications(db, sample_contraindication_categories):
    """Создает тестовые противопоказания."""
    cat_chronic, cat_allergy, cat_immuno, cat_pregnancy, cat_acute = sample_contraindication_categories

    data = [
        ('Бронхиальная астма', cat_chronic, 'Заболевания дыхательной системы', 85, 10),
        ('ХОБЛ', cat_chronic, 'Заболевания дыхательной системы', 70, 5),
        ('Сахарный диабет', cat_chronic, 'Эндокринные заболевания', 75, 8),
        ('Анафилактический шок', cat_allergy, None, 95, 20),
        ('Аллергия на компоненты вакцины', cat_allergy, None, 90, 15),
        ('Аллергия на белок куриного яйца', cat_allergy, None, 80, 12),
        ('ВИЧ-инфекция', cat_immuno, None, 80, 8),
        ('Первичный иммунодефицит', cat_immuno, None, 75, 6),
        ('Беременность', cat_pregnancy, None, 88, 12),
        ('Период грудного вскармливания', cat_pregnancy, None, 65, 7),
        ('Острое ОРВИ с температурой выше 38°C', cat_acute, None, 60, 3),
        ('Острые инфекционные заболевания', cat_acute, None, 55, 2),
    ]

    contraindications = []
    for name, category, subcategory, search_weight, search_count in data:
        c = Contraindication.objects.create(
            name=name,
            subcategory=subcategory,
            search_weight=search_weight,
            search_select_count=search_count,
        )
        c.categories.add(category)
        contraindications.append(c)

    return contraindications


@pytest.fixture
def sample_official_instructions(db):
    """Создает тестовые официальные инструкции."""
    instructions = [
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине АКДС',
            url='https://grls.rosminzdrav.ru/instruction/akds',
            source='ГРЛС',
            description='Официальная инструкция по применению вакцины АКДС',
            search_weight=85,
            search_select_count=10,
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине БЦЖ',
            url='https://grls.rosminzdrav.ru/instruction/bczh',
            source='ГРЛС',
            description='Официальная инструкция по применению вакцины БЦЖ',
            search_weight=70,
            search_select_count=5,
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине Гепатит B',
            url='https://grls.rosminzdrav.ru/instruction/hepatitis-b',
            source='Минздрав',
            description='Инструкция Минздрава по вакцине Гепатит B',
            search_weight=90,
            search_select_count=15,
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине Корь',
            url='https://grls.rosminzdrav.ru/instruction/kor',
            source='ГРЛС',
            description='',
            search_weight=60,
            search_select_count=3,
        ),
    ]
    return instructions
