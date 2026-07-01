import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from contraindications.models import Contraindication
from reference_books.models import CategoryInfection, Infection, Ingredients, MethodsOfAdministration

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Создает тестового пользователя."""
    user = User.objects.create_user(
        username='test_user',
        password='test123',
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def auth_client(api_client, test_user):
    """Аутентифицированный клиент."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def test_data(db):
    """Создает тестовые справочные данные."""
    category = CategoryInfection.objects.create(name='national_calendar')
    infections = [
        Infection.objects.create(name='Дифтерия', category=category),
        Infection.objects.create(name='Столбняк', category=category),
        Infection.objects.create(name='Коклюш', category=category),
    ]
    ingredients = [
        Ingredients.objects.create(name='Антиген дифтерийный', type='active'),
        Ingredients.objects.create(name='Алюминия гидроксид', type='excipient'),
    ]
    contraindications = [
        Contraindication.objects.create(name='Аллергия на компоненты'),
        Contraindication.objects.create(name='Острое заболевание'),
    ]
    administration_methods = [
        MethodsOfAdministration.objects.create(
            name='Внутримышечно', list_icon_url='test/icon1.png', detail_image_url='test/detail1.png'
        ),
        MethodsOfAdministration.objects.create(
            name='Подкожно', list_icon_url='test/icon2.png', detail_image_url='test/detail2.png'
        ),
    ]
    return {
        'infections': infections,
        'ingredients': ingredients,
        'contraindications': contraindications,
        'administration_methods': administration_methods,
    }


@pytest.fixture
def admin_vaccines_card_url():
    """Возвращает админский урл карточки."""
    return reverse('admin-vaccine-cards')


@pytest.fixture
def minimal_vaccine_payload():
    """Создает минимальный payload для создания карточки вакцины."""
    return {
        'name': 'Минимальная вакцина',
        'official_name': 'Минимальная вакцина',
        'is_available_in_rf': 'true',
        'infection_ids': [],
        'ingredients': [],
        'contraindications': [],
        'administration_methods': [],
        'comment': {},
    }
