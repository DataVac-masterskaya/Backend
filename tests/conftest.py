import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from contraindications.models import Contraindication, ContraindicationCategory
from instructions.models import OfficialInstruction
from reference_books.models import CategoryInfection, Infection, Ingredients
from vaccines.models import VaccineCard, VaccineCardVersion

User = get_user_model()


@pytest.fixture
def api_client():
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def sample_infections(db):
    """Создает инфекции и их категории для pytest-тестов."""
    category1 = CategoryInfection.objects.create(name='virusnye')
    category2 = CategoryInfection.objects.create(name='bakterialnye')

    infections = [
        Infection.objects.create(name='Гепатит B', category=category1),
        Infection.objects.create(name='Туберкулез', category=category2),
        Infection.objects.create(name='Корь', category=category1),
        Infection.objects.create(name='Дифтерия', category=category2),
    ]
    return infections


@pytest.fixture
def sample_categories(db):
    """Создает категории противопоказаний для pytest-тестов."""
    category1 = ContraindicationCategory.objects.create(name='Абсолютные')
    category2 = ContraindicationCategory.objects.create(name='Относительные')
    return [category1, category2]


@pytest.fixture
def sample_contraindications(db, sample_categories):
    """Создает противопоказания с привязкой к категориям для pytest-тестов."""
    category1, category2 = sample_categories

    contraindication1 = Contraindication.objects.create(name='Аллергия на компоненты')
    contraindication1.categories.add(category1)

    contraindication2 = Contraindication.objects.create(name='Беременность')
    contraindication2.categories.add(category2)

    return [contraindication1, contraindication2]


@pytest.fixture
def sample_ingredients(db):
    """Создает ингредиенты для pytest-тестов."""
    ingredients = [
        Ingredients.objects.create(name='Алюминия гидроксид', type='Вспомогательное вещество'),
        Ingredients.objects.create(name='Анатоксин дифтерийный', type='Действующее вещество'),
        Ingredients.objects.create(name='Анатоксин столбнячный', type='Действующее вещество'),
    ]
    return ingredients


@pytest.fixture
def test_user(db):
    """Тестовый пользователь."""
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def sample_vaccine_versions(db, test_user):
    """Создает версии карточек вакцин с карточками."""
    versions = []
    for i, name in enumerate(['АКДС', 'БЦЖ', 'Гепатит B', 'Корь', 'Полиомиелит', 'АДС-М']):
        vaccine_card = VaccineCard.objects.create(
            status='active',
            is_visible=True,
            created_by=test_user,
        )

        version = VaccineCardVersion.objects.create(
            vaccine_card=vaccine_card,
            version_number=1,
            name=name,
            official_name=f'Официальное название {name}',
            pdf_url=f'https://grls.rosminzdrav.ru/pdf/{name.lower()}',
            ohlp_url=f'https://grls.rosminzdrav.ru/{name.lower()}',
            nonspec_url=f'https://instructions.ru/patient/{name.lower()}',
            instruction_url=f'https://instructions.ru/specialist/{name.lower()}',
            created_by=test_user,
        )

        vaccine_card.current_version = version
        vaccine_card.published_version = version
        vaccine_card.save()

        versions.append(version)

    return versions


@pytest.fixture
def sample_vaccine_card_with_versions(db, test_user):
    """Создает одну карточку вакцины с несколькими версиями."""
    vaccine_card = VaccineCard.objects.create(
        status='active',
        is_visible=True,
        created_by=test_user,
    )

    versions = []
    for i in range(3):
        version = VaccineCardVersion.objects.create(
            vaccine_card=vaccine_card,
            version_number=i + 1,
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
def sample_official_instructions(db):
    """Создает тестовые официальные инструкции."""
    instructions = [
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине АКДС',
            url='https://grls.rosminzdrav.ru/instruction/akds',
            source='ГРЛС',
            description='Официальная инструкция по применению вакцины АКДС',
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине БЦЖ',
            url='https://grls.rosminzdrav.ru/instruction/bczh',
            source='ГРЛС',
            description='Официальная инструкция по применению вакцины БЦЖ',
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине Гепатит B',
            url='https://grls.rosminzdrav.ru/instruction/hepatitis-b',
            source='Минздрав',
            description='Инструкция Минздрава по вакцине Гепатит B',
        ),
        OfficialInstruction.objects.create(
            title='Инструкция к вакцине Корь',
            url='https://grls.rosminzdrav.ru/instruction/kor',
            source='ГРЛС',
            description='',
        ),
    ]
    return instructions
