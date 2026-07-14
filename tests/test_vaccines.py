from urllib.parse import urlencode

import pytest
from django.urls import reverse

from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db


class TestVaccineList:
    """Тесты для /vaccines/."""

    URL_LIST = 'vaccine-list'

    def test_list_vaccines(self, api_client, sample_vaccine_versions):
        """Получение списка вакцин."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}'
        )
        data = response.json()
        assert len(data) == len(sample_vaccine_versions), (
            f'Ожидалось {len(sample_vaccine_versions)} вакцин, '
            f'получено {len(data)}. Данные: {data}'
        )

    def test_sort_by_name_asc(self, api_client, sample_vaccine_versions):
        """Сортировка по name asc."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name', 'direction': 'asc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f'Сортировка по name asc не работает. '
            f'Ожидалось: {expected}, получено: {names}. '
            f'Параметры: {params}'
        )

    def test_sort_by_name_desc(self, api_client, sample_vaccine_versions):
        """Сортировка по name desc."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name', 'direction': 'desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names, reverse=True)
        assert names == expected, (
            f'Сортировка по name desc не работает. '
            f'Ожидалось: {expected}, получено: {names}. '
            f'Параметры: {params}'
        )

    def test_sort_by_official_name_asc(self, api_client, sample_vaccine_versions):
        """Сортировка по official_name asc."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'official_name', 'direction': 'asc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        official_names = [item['official_name'] for item in data]
        expected = sorted(official_names)
        assert official_names == expected, (
            f'Сортировка по official_name asc не работает. '
            f'Ожидалось: {expected}, получено: {official_names}. '
            f'Параметры: {params}'
        )

    def test_sort_by_official_name_desc(self, api_client, sample_vaccine_versions):
        """Сортировка по official_name desc."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'official_name', 'direction': 'desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        official_names = [item['official_name'] for item in data]
        expected = sorted(official_names, reverse=True)
        assert official_names == expected, (
            f'Сортировка по official_name desc не работает. '
            f'Ожидалось: {expected}, получено: {official_names}. '
            f'Параметры: {params}'
        )

    def test_sort_invalid_sort_by(self, api_client):
        """Некорректное поле для сортировки."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'invalid_field', 'direction': 'asc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code in [400, 200], (
            f'Ожидался статус 400 или 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )

    def test_sort_invalid_direction(self, api_client):
        """Некорректное значение direction."""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name', 'direction': 'invalid'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code in [400, 200], (
            f'Ожидался статус 400 или 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )

    def test_filter_by_first_letter(self, api_client, sample_vaccine_versions):
        """Фильтрация по первой букве через query-параметр first_letter."""
        url = reverse(self.URL_LIST)
        params = {'first_letter': 'А'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) > 0, (
            f'Ожидался хотя бы 1 результат для first_letter=А, '
            f'получено {len(data)} результатов. Данные: {data}'
        )
        for item in data:
            assert item['name'].startswith('А'), (
                f'Ожидалось имя, начинающееся на "А", '
                f'получено \'{item["name"]}\'. Данные: {item}'
            )

    def test_filter_by_first_letter_lowercase(self, api_client, sample_vaccine_versions):
        """Фильтрация по первой букве (нижний регистр) через query-параметр."""
        url = reverse(self.URL_LIST)
        params = {'first_letter': 'а'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        if len(data) > 0:
            for item in data:
                assert item['name'].startswith('А'), (
                    f'Ожидалось имя, начинающееся на "А" (регистронезависимо), '
                    f'получено \'{item["name"]}\'. Данные: {item}'
                )

    def test_filter_by_first_letter_no_results(self, api_client):
        """Фильтрация по букве без результатов через query-параметр."""
        url = reverse(self.URL_LIST)
        params = {'first_letter': 'Я'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) == 0, (
            f'Ожидался пустой список для first_letter=Я, '
            f'получено {len(data)} записей. Данные: {data}'
        )

    def test_filter_by_first_letter_different_letters(self, api_client, sample_vaccine_versions):
        """Фильтрация по разным буквам через query-параметр."""
        url = reverse(self.URL_LIST)

        # Проверяем фильтрацию по букве 'Г'
        params = {'first_letter': 'Г'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) > 0, (
            f'Ожидался хотя бы 1 результат для first_letter=Г, '
            f'получено {len(data)} результатов. Данные: {data}'
        )
        for item in data:
            assert item['name'].startswith('Г'), (
                f'Ожидалось имя, начинающееся на "Г", '
                f'получено \'{item["name"]}\'. Данные: {item}'
            )

    def test_combined_sort_and_filter(self, api_client, sample_vaccine_versions):
        """Комбинация сортировки и фильтрации через query-параметры."""
        url = reverse(self.URL_LIST)
        params = {
            'sort_by': 'name',
            'direction': 'desc',
            'first_letter': 'А'
        }
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, params: {params}'
        )
        data = response.json()
        for item in data:
            assert item['name'].startswith('А'), (
                f'Фильтрация по первой букве нарушена. '
                f'Ожидалось имя на "А", получено \'{item["name"]}\'. '
                f'Данные: {item}'
            )
        names = [item['name'] for item in data]
        expected = sorted(names, reverse=True)
        assert names == expected, (
            f'Сортировка по убыванию нарушена при комбинированном запросе. '
            f'Ожидалось: {expected}, получено: {names}. '
            f'params: {params}'
        )

    def test_only_visible_vaccines(self, api_client, test_user):
        """Проверка, что видны только is_visible=True вакцины."""
        visible_card = VaccineCard.objects.create(
            status='active',
            is_visible=True,
            created_by=test_user,
        )
        visible_version = VaccineCardVersion.objects.create(
            vaccine_card=visible_card,
            version_number=1,
            name='Видимая вакцина',
            official_name='Официальное название',
            created_by=test_user,
        )
        visible_card.current_version = visible_version
        visible_card.published_version = visible_version
        visible_card.save()

        hidden_card = VaccineCard.objects.create(
            status='active',
            is_visible=False,
            created_by=test_user,
        )
        hidden_version = VaccineCardVersion.objects.create(
            vaccine_card=hidden_card,
            version_number=1,
            name='Скрытая вакцина',
            official_name='Официальное название скрытой',
            created_by=test_user,
        )
        hidden_card.current_version = hidden_version
        hidden_card.save()

        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        names = [item['name'] for item in data]
        assert 'Видимая вакцина' in names, (
            f'Видимая вакцина должна быть в списке. Данные: {names}'
        )
        assert 'Скрытая вакцина' not in names, (
            f'Скрытая вакцина не должна быть в списке. Данные: {names}'
        )


class TestVaccineDetail:
    """Тесты для /vaccines/{id}."""

    URL_DETAIL = 'vaccine-detail'

    def test_get_full_card(self, api_client, sample_vaccine_versions):
        """Получение полной карточки вакцины."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(url)

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, card_id={version.vaccine_card.id}'
        )
        data = response.json()
        assert data['name'] == version.name, (
            f'Ожидалось имя \'{version.name}\', '
            f'получено \'{data.get("name")}\'. Данные: {data}'
        )
        assert data['official_name'] == version.official_name, (
            f'Ожидалось official_name \'{version.official_name}\', '
            f'получено \'{data.get("official_name")}\'. Данные: {data}'
        )

    def test_get_full_card_with_versions(self, api_client, sample_vaccine_card_with_versions):
        """Получение карточки с несколькими версиями."""
        vaccine_card, versions = sample_vaccine_card_with_versions
        url = reverse(self.URL_DETAIL, kwargs={'pk': vaccine_card.id})
        response = api_client.get(url)

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}, card_id={vaccine_card.id}'
        )
        data = response.json()
        assert data['name'] == versions[-1].name, (
            f'Ожидалось имя последней версии \'{versions[-1].name}\', '
            f'получено \'{data.get("name")}\'. Данные: {data}'
        )

    def test_get_nonexistent_vaccine(self, api_client):
        """Запрос несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == 404, (
            f'Ожидался статус 404 для несуществующей вакцины, '
            f'получен {response.status_code}. URL: {url}'
        )

    def test_get_hidden_vaccine(self, api_client, test_user):
        """Запрос скрытой вакцины (is_visible=False)."""
        hidden_card = VaccineCard.objects.create(
            status='active',
            is_visible=False,
            created_by=test_user,
        )
        hidden_version = VaccineCardVersion.objects.create(
            vaccine_card=hidden_card,
            version_number=1,
            name='Скрытая вакцина',
            official_name='Официальное название',
            created_by=test_user,
        )
        hidden_card.current_version = hidden_version
        hidden_card.published_version = hidden_version
        hidden_card.save()

        url = reverse(self.URL_DETAIL, kwargs={'pk': hidden_card.id})
        response = api_client.get(url)

        assert response.status_code in [404, 403], (
            f'Ожидался статус 404 или 403 для скрытой вакцины, '
            f'получен {response.status_code}. URL: {url}'
        )


class TestVaccinePdf:
    """Тесты для /vaccines/{id}/pdf."""

    URL_DETAIL = 'vaccine-detail'

    def test_get_pdf_url(self, api_client, sample_vaccine_versions):
        """Получение ссылки на PDF."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}pdf/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}pdf/, card_id={version.vaccine_card.id}'
        )
        data = response.json()
        assert 'pdf_url' in data, (
            f'Ожидалось поле \'pdf_url\' в ответе. '
            f'Ключи: {list(data.keys())}'
        )
        assert data['pdf_url'] == version.pdf_url, (
            f'Ожидалась ссылка \'{version.pdf_url}\', '
            f'получена \'{data.get("pdf_url")}\'. Данные: {data}'
        )

    def test_get_pdf_url_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на PDF."""
        version = sample_vaccine_versions[1]
        version.pdf_url = ''
        version.save()

        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}pdf/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}pdf/'
        )
        data = response.json()
        assert data['pdf_url'] == '', (
            f'Ожидалась пустая строка, '
            f'получено \'{data.get("pdf_url")}\'. Данные: {data}'
        )

    def test_get_pdf_nonexistent_vaccine(self, api_client):
        """PDF для несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(f'{url}pdf/')

        assert response.status_code == 404, (
            f'Ожидался статус 404, получен {response.status_code}. '
            f'URL: {url}pdf/'
        )


class TestVaccineOfficialLink:
    """Тесты для /vaccines/{id}/official-link."""

    URL_DETAIL = 'vaccine-detail'

    def test_get_ohlp_url(self, api_client, sample_vaccine_versions):
        """Получение ссылки на ГРЛС."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}official-link/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}official-link/, card_id={version.vaccine_card.id}'
        )
        data = response.json()
        assert 'ohlp_url' in data, (
            f'Ожидалось поле \'ohlp_url\' в ответе. '
            f'Ключи: {list(data.keys())}'
        )
        assert data['ohlp_url'] == version.ohlp_url, (
            f'Ожидалась ссылка \'{version.ohlp_url}\', '
            f'получена \'{data.get("ohlp_url")}\'. Данные: {data}'
        )

    def test_get_ohlp_url_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на ГРЛС."""
        version = sample_vaccine_versions[1]
        version.ohlp_url = ''
        version.save()

        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}official-link/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}official-link/'
        )
        data = response.json()
        assert data['ohlp_url'] == '', (
            f'Ожидалась пустая строка, '
            f'получено \'{data.get("ohlp_url")}\'. Данные: {data}'
        )

    def test_get_ohlp_nonexistent_vaccine(self, api_client):
        """Ссылка для несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(f'{url}official-link/')

        assert response.status_code == 404, (
            f'Ожидался статус 404, получен {response.status_code}. '
            f'URL: {url}official-link/'
        )


class TestVaccineInstructionPatient:
    """Тесты для /vaccines/{id}/instruction-patient."""

    URL_DETAIL = 'vaccine-detail'

    def test_get_nonspec_url(self, api_client, sample_vaccine_versions):
        """Получение ссылки на инструкцию для пациента."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}instruction-patient/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}instruction-patient/, card_id={version.vaccine_card.id}'
        )
        data = response.json()
        assert 'nonspec_url' in data, (
            f'Ожидалось поле \'nonspec_url\' в ответе. '
            f'Ключи: {list(data.keys())}'
        )
        assert data['nonspec_url'] == version.nonspec_url, (
            f'Ожидалась ссылка \'{version.nonspec_url}\', '
            f'получена \'{data.get("nonspec_url")}\'. Данные: {data}'
        )

    def test_get_nonspec_url_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на инструкцию для пациента."""
        version = sample_vaccine_versions[1]
        version.nonspec_url = ''
        version.save()

        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}instruction-patient/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}instruction-patient/'
        )
        data = response.json()
        assert data['nonspec_url'] == '', (
            f'Ожидалась пустая строка, '
            f'получено \'{data.get("nonspec_url")}\'. Данные: {data}'
        )

    def test_get_nonspec_nonexistent_vaccine(self, api_client):
        """Инструкция для несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(f'{url}instruction-patient/')

        assert response.status_code == 404, (
            f'Ожидался статус 404, получен {response.status_code}. '
            f'URL: {url}instruction-patient/'
        )


class TestVaccineInstructionSpecialist:
    """Тесты для /vaccines/{id}/instruction-specialist."""

    URL_DETAIL = 'vaccine-detail'

    def test_get_instruction_url(self, api_client, sample_vaccine_versions):
        """Получение ссылки на инструкцию для специалиста."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}instruction-specialist/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}instruction-specialist/, card_id={version.vaccine_card.id}'
        )
        data = response.json()
        assert 'instruction_url' in data, (
            f'Ожидалось поле \'instruction_url\' в ответе. '
            f'Ключи: {list(data.keys())}'
        )
        assert data['instruction_url'] == version.instruction_url, (
            f'Ожидалась ссылка \'{version.instruction_url}\', '
            f'получена \'{data.get("instruction_url")}\'. Данные: {data}'
        )

    def test_get_instruction_url_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на инструкцию для специалиста."""
        version = sample_vaccine_versions[1]
        version.instruction_url = ''
        version.save()

        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(f'{url}instruction-specialist/')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. '
            f'URL: {url}instruction-specialist/'
        )
        data = response.json()
        assert data['instruction_url'] == '', (
            f'Ожидалась пустая строка, '
            f'получено \'{data.get("instruction_url")}\'. Данные: {data}'
        )

    def test_get_instruction_nonexistent_vaccine(self, api_client):
        """Инструкция для несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(f'{url}instruction-specialist/')

        assert response.status_code == 404, (
            f'Ожидался статус 404, получен {response.status_code}. '
            f'URL: {url}instruction-specialist/'
        )
