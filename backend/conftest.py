import pytest
from accounts.models import RoleChoices
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from contraindications.models import Contraindication
from reference_books.models import CategoryInfection, Infection, Ingredients, MethodsOfAdministration
from vaccines.models import (
    VaccineCard,
    VaccineCardVersion,
    VaccineCardVersionContraindication,
)

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Создает тестового пользователя."""
    user = User.objects.create_user(
        username='test_user', password='test123', is_staff=True, is_superuser=True, role=RoleChoices.MODERATOR
    )
    return user


@pytest.fixture
def auth_client(api_client, test_user):
    """Аутентифицированный клиент."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def infection_category():
    """Создает категорию инфекций для тестовых записей."""
    return CategoryInfection.objects.create(name='viral')


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
def published_vaccine_factory(test_user):
    """Создает опубликованную карточку вакцины для тестов."""

    def factory(
        name='Вакцина АДС-М',
        official_name='Анатоксин дифтерийно-столбнячный',
        is_visible=True,
        contraindication=None,
        min_age_days=6,
        max_age_days=18,
        age_allowed='от 0 дней до 99999',
    ):
        vaccine_card = VaccineCard.objects.create(is_visible=is_visible)
        version = VaccineCardVersion.objects.create(
            vaccine_card=vaccine_card,
            name=name,
            official_name=official_name,
            age_allowed=age_allowed,
            min_age_days=min_age_days,
            max_age_days=max_age_days,
            pregnancy_usage_status=True,
            created_by=test_user,
            pdf_url='https://datavac.vaccina.info/vaccines/Pentaxim/',
            instruction_url='https://datavac.vaccina.info/vaccines/Pentaxim/',
            nonspec_url='https://datavac.vaccina.info/vaccines/Pentaxim/',
            ohlp_url='https://datavac.vaccina.info/vaccines/Pentaxim/',
        )
        vaccine_card.published_version = version
        vaccine_card.current_version = version
        vaccine_card.save(update_fields=('published_version', 'current_version'))
        if contraindication:
            VaccineCardVersionContraindication.objects.create(
                vaccine_card_version=version,
                contraindication=contraindication,
            )
        return vaccine_card

    return factory


@pytest.fixture
def vaccine_with_contraindication(published_vaccine_factory):
    """Создает опубликованную вакцину, связанную с противопоказанием."""
    contraindication = Contraindication.objects.create(name='Аллергия')
    vaccine_card = published_vaccine_factory(contraindication=contraindication)
    return {
        'contraindication': contraindication,
        'vaccine_card': vaccine_card,
    }


@pytest.fixture
def admin_vaccines_card_url():
    """Возвращает админский урл карточки."""
    return reverse('admin-vaccine-cards')


@pytest.fixture
def contraindication_vaccines_url():
    """Возвращает URL списка вакцин по противопоказанию."""

    def build_url(contraindication_id):
        return reverse('contraindication-vaccines', kwargs={'pk': contraindication_id})

    return build_url


@pytest.fixture
def search_suggestions_url():
    """Возвращает URL глобальных поисковых подсказок."""
    return reverse('search-suggestions')


@pytest.fixture
def search_select_url():
    """Возвращает URL фиксации выбора поисковой подсказки."""
    return reverse('search-select')


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


@pytest.fixture
def minimal_vaccine_payload_update():
    """Создает минимальный payload для редактирования карточки вакцины."""
    return {
        'name': 'Измененная вакцина',
        'official_name': 'Измененная вакцина',
        'is_available_in_rf': 'false',
        'infection_ids': [],
        'ingredients': [],
        'contraindications': [],
        'administration_methods': [],
        'comment': {},
        'status': 'active',
    }


@pytest.fixture
def vaccine_detail_url():
    """Возвращает URL для детального просмотра/обновления карточки."""

    def get_url(vaccine_id):
        return reverse('admin-vaccine-detail', args=[vaccine_id])

    return get_url


@pytest.fixture
def login_url():
    """URL получения JWT-токена."""
    return reverse('token_obtain')


@pytest.fixture
def refresh_url():
    """URL обновления JWT-токена."""
    return reverse('token_refresh')


@pytest.fixture
def data_for_success_auth(test_user):
    """Корректные данные для аутентификации."""
    return {'username': test_user.username, 'password': 'test123'}


@pytest.fixture
def data_wrong_password(test_user):
    """Данные для аутентификации с неверным паролем."""
    return {'username': test_user.username, 'password': 'wrong_password123'}


@pytest.fixture
def vaccine_list_url():
    """Возвращает URL списка вакцин (публичный)."""
    return reverse('publish-vaccine')


@pytest.fixture
def vaccine_publish_detail_url():
    """Возвращает URL для детального просмотра (публичный)."""

    def get_url(id):
        return reverse('publish-vaccine-detail', args=[id])

    return get_url


@pytest.fixture
def vaccine_pdf_url():
    """Возвращает URL для pdf по ID."""

    def get_url(vaccine_id):
        return reverse('vaccine-pdf', args=[vaccine_id])

    return get_url


@pytest.fixture
def vaccine_instruction_url():
    """Возвращает URL для инструкции по ID."""

    def get_url(vaccine_id):
        return reverse('official-link', args=[vaccine_id])

    return get_url


@pytest.fixture
def vaccine_instruction_patient_url():
    """Возвращает URL инструкции для пациентов по ID."""

    def get_url(vaccine_id):
        return reverse('instruction-patient', args=[vaccine_id])

    return get_url


@pytest.fixture
def vaccine_instruction_specialist_url():
    """Возвращает URL инструкции для пациентов по ID."""

    def get_url(vaccine_id):
        return reverse('instruction-specialist', args=[vaccine_id])

    return get_url
