import re
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from utils import get_results

from vaccines.models import VaccineCard, VaccineCardVersion

pytestmark = pytest.mark.django_db


class TestVaccineList:
    """Тесты для /vaccines с query-параметрами."""

    URL_LIST = 'publish-vaccine'

    def test_list_vaccines(self, api_client, sample_vaccine_versions):
        """Получение списка вакцин с проверкой структуры."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        assert len(results) == len(sample_vaccine_versions), (
            f'Ожидалось {len(sample_vaccine_versions)} вакцин, получено {len(results)}. Данные: {results}'
        )

        item = results[0]

        assert isinstance(item['id'], int), f'id должен быть int, получен {type(item["id"])}: {item["id"]}'
        assert isinstance(item['name'], str) and len(item['name']) > 0, (
            f'name должен быть непустой строкой, получен {type(item["name"])}: {item["name"]}'
        )
        assert isinstance(item['official_name'], str), (
            f'official_name должен быть строкой, получен {type(item["official_name"])}'
        )
        assert isinstance(item['is_available_in_rf'], bool), (
            f'is_available_in_rf должен быть bool, получен {type(item["is_available_in_rf"])}: '
            f'{item["is_available_in_rf"]}'
        )
        assert isinstance(item['popularity'], int), (
            f'popularity должен быть int, получен {type(item["popularity"])}: {item["popularity"]}'
        )

        for field in ['min_age_months', 'max_age_months']:
            assert field in item, f'Ожидалось поле "{field}" в элементе. Ключи: {list(item.keys())}'
            if item[field] is not None:
                assert isinstance(item[field], int), (
                    f'{field} должен быть int или null, получен {type(item[field])}: {item[field]}'
                )

        pregnancy = item.get('pregnancy_usage_status')
        assert pregnancy in [True, False, 'True', 'False', None], (
            f'pregnancy_usage_status должен быть bool или null, получен {type(pregnancy)}: {pregnancy}'
        )

        assert isinstance(item.get('infections', []), list), (
            f'infections должен быть списком, получен {type(item.get("infections"))}'
        )
        for infection in item['infections']:
            assert isinstance(infection['id'], int), (
                f'id инфекции должен быть int, получен {type(infection["id"])}: {infection["id"]}'
            )
            assert isinstance(infection['name'], str), (
                f'name инфекции должен быть строкой, получен {type(infection["name"])}'
            )

        valid_codes = [
            'intramuscularly',
            'subcutaneously',
            'cutaneously',
            'intradermally',
            'drops',
            'pills',
            'intranasally',
        ]
        assert isinstance(item.get('administration_methods', []), list), 'administration_methods должен быть списком'
        for method in item['administration_methods']:
            assert 'code' in method, f'Ожидалось поле "code" в методе введения. Ключи: {list(method.keys())}'
            assert method['code'] in valid_codes, (
                f'Недопустимый код метода: {method.get("code")}. Допустимые: {valid_codes}'
            )
            assert 'age_group' in method, f'Ожидалось поле "age_group" в методе введения. Ключи: {list(method.keys())}'
            assert method['age_group'] is None or isinstance(method['age_group'], str), (
                f'age_group должен быть строкой или null, получен {type(method["age_group"])}: {method["age_group"]}'
            )
            assert 'note' in method, f'Ожидалось поле "note" в методе введения. Ключи: {list(method.keys())}'
            assert method['note'] is None or isinstance(method['note'], str), (
                f'note должен быть строкой или null, получен {type(method["note"])}: {method["note"]}'
            )

    def test_sort_by_popularity(self, api_client, sample_vaccine_versions):
        """Сортировка по popularity."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'popularity'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) == len(sample_vaccine_versions), (
            f'Ожидалось {len(sample_vaccine_versions)} вакцин, получено {len(results)}'
        )
        if len(results) > 1:
            popularity_values = [item['popularity'] for item in results]
            assert popularity_values == sorted(popularity_values, reverse=True), (
                f'Сортировка по popularity (DESC) нарушена. '
                f'Ожидалось: {sorted(popularity_values, reverse=True)}, '
                f'получено: {popularity_values}'
            )

    def test_sort_by_name(self, api_client, sample_vaccine_versions):
        """Сортировка по name."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'name'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names), (
            f'Сортировка по name (ASC) нарушена. Ожидалось: {sorted(names)}, получено: {names}'
        )

    def test_sort_by_name_desc(self, api_client, sample_vaccine_versions):
        """Сортировка по name_desc."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'name_desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names, reverse=True), (
            f'Сортировка по name (DESC) нарушена. Ожидалось: {sorted(names, reverse=True)}, получено: {names}'
        )

    def test_search_by_q(self, api_client, sample_vaccine_versions):
        """Поиск по названию через параметр q."""
        url = reverse(self.URL_LIST)

        params = {'q': 'Инфанрикс'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, f'Поиск по "Инфанрикс" не вернул результатов. Данные: {data}'
        for item in results:
            assert 'Инфанрикс' in item['name'] or 'инфанрикс' in item['name'].lower(), (
                f'Вакцина "{item["name"]}" не содержит "Инфанрикс". params: {params}'
            )

        params = {'q': 'НесуществующаяВакцина'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f'Ожидался пустой список для поиска "НесуществующаяВакцина", '
            f'получено {len(results)} записей. Данные: {results}'
        )

    def test_filter_by_letter(self, api_client, sample_vaccine_versions):
        """Фильтрация по первой букве через параметр letter."""
        url = reverse(self.URL_LIST)

        params = {'letter': 'И'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, f'Фильтр по letter=И не вернул результатов. Данные: {data}'
        for item in results:
            assert item['name'].startswith('И'), f'Вакцина "{item["name"]}" не начинается на "И". params: {params}'

        params = {'letter': 'и'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        if len(results) > 0:
            for item in results:
                assert item['name'].startswith('И'), (
                    f'Вакцина "{item["name"]}" не начинается на "И" (нижний регистр). params: {params}'
                )

        params = {'letter': 'Я'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f'Ожидался пустой список для letter=Я, получено {len(results)} записей. Данные: {results}'
        )

    def test_filter_by_infection_id(self, api_client, sample_vaccine_versions, sample_infections):
        """Фильтрация по infection_id."""
        infection = sample_infections[0]
        url = reverse(self.URL_LIST)
        params = {'infection_id': infection.id}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, (
            f'Фильтр по infection_id={infection.id} ({infection.name}) не вернул результатов. Данные: {data}'
        )
        for item in results:
            infection_ids = [inf['id'] for inf in item.get('infections', [])]
            assert infection.id in infection_ids, (
                f"Вакцина '{item['name']}' не содержит инфекцию {infection.id} "
                f'({infection.name}). Инфекции вакцины: {infection_ids}'
            )

    def test_filter_by_infection_id_no_results(self, api_client):
        """Фильтрация по несуществующему infection_id."""
        url = reverse(self.URL_LIST)
        params = {'infection_id': 99999}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f'Ожидался пустой список для infection_id=99999, получено {len(results)} записей. Данные: {results}'
        )

    def test_filter_by_ingredient_id(self, api_client, sample_vaccine_versions):
        """Фильтрация по ingredient_id."""
        url = reverse(self.URL_LIST)
        params = {'ingredient_id': 1}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert isinstance(results, list), f'Ожидался список, получен {type(results)}'

    def test_filter_by_ingredient_id_no_results(self, api_client):
        """Фильтрация по несуществующему ingredient_id."""
        url = reverse(self.URL_LIST)
        params = {'ingredient_id': 99999}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f'Ожидался пустой список для ingredient_id=99999, получено {len(results)} записей. Данные: {results}'
        )

    def test_filter_by_contraindication_id(self, api_client, sample_vaccine_versions):
        """Фильтрация по contraindication_id."""
        url = reverse(self.URL_LIST)
        params = {'contraindication_id': 1}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert isinstance(results, list), f'Ожидался список, получен {type(results)}'

    def test_filter_by_contraindication_id_no_results(self, api_client):
        """Фильтрация по несуществующему contraindication_id."""
        url = reverse(self.URL_LIST)
        params = {'contraindication_id': 99999}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f'Ожидался пустой список для contraindication_id=99999, получено {len(results)} записей. Данные: {results}'
        )

    def test_pagination(self, api_client, sample_vaccine_versions):
        """Пагинация через limit и offset."""
        url = reverse(self.URL_LIST)

        params = {'limit': 1}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) == 1, f'Ожидался 1 элемент (limit=1), получено {len(results)}. Данные: {results}'

        params = {'limit': 1, 'offset': 1}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) == 1, f'Ожидался 1 элемент (limit=1, offset=1), получено {len(results)}'
        assert results[0]['name'] != sample_vaccine_versions[0].name, (
            f'Offset не сработал: первый элемент тот же, что и без offset. Имя: {results[0]["name"]}'
        )

    def test_combined_params(self, api_client, sample_vaccine_versions):
        """Комбинация нескольких параметров."""
        url = reverse(self.URL_LIST)
        params = {
            'sort': 'name_desc',
            'letter': 'А',
            'limit': 2,
        }
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()
        results = get_results(data)
        assert len(results) <= 2, f'Ожидалось не более 2 элементов (limit=2), получено {len(results)}'
        for item in results:
            assert item['name'].startswith('А'), f'Фильтр по букве "А" нарушен: "{item["name"]}". params: {params}'
        names = [item['name'] for item in results]
        assert names == sorted(names, reverse=True), (
            f'Сортировка по name_desc нарушена. Ожидалось: {sorted(names, reverse=True)}, получено: {names}'
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
        results = get_results(data)
        names = [item['name'] for item in results]
        assert 'Видимая вакцина' in names, f'Видимая вакцина не найдена в ответе. Имена: {names}'
        assert 'Скрытая вакцина' not in names, f'Скрытая вакцина не должна быть в ответе. Имена: {names}'


class TestVaccineDetail:
    """Тесты для /vaccines/{id} — полная карточка вакцины."""

    URL_DETAIL = 'publish-vaccine-detail'

    def test_get_full_card(self, api_client, sample_vaccine_versions):
        """Получение полной карточки вакцины с проверкой значений и типов."""
        version = sample_vaccine_versions[0]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()

        assert data['id'] == version.vaccine_card.id, f'Ожидался id={version.vaccine_card.id}, получен {data.get("id")}'
        assert data['name'] == version.name, f'Ожидалось name="{version.name}", получено "{data.get("name")}"'
        assert data['official_name'] == version.official_name, (
            f'Ожидалось official_name="{version.official_name}", получено "{data.get("official_name")}"'
        )

        assert isinstance(data['is_available_in_rf'], bool), (
            f'is_available_in_rf должен быть bool, '
            f'получен {type(data["is_available_in_rf"])}: {data["is_available_in_rf"]}'
        )

        if data.get('revision_date') is not None:
            assert re.match(r'^\d{4}-\d{2}-\d{2}$', data['revision_date']), (
                f'revision_date должен быть в формате YYYY-MM-DD, получено: {data["revision_date"]}'
            )

        pregnancy = data.get('pregnancy_usage_status')
        assert pregnancy in [True, False, 'True', 'False', None], (
            f'pregnancy_usage_status должен быть bool или null, получен {type(pregnancy)}: {pregnancy}'
        )

        for age_field in ['min_age_months', 'max_age_months']:
            if data.get(age_field) is not None:
                assert isinstance(data[age_field], int), (
                    f'{age_field} должен быть int, получен {type(data[age_field])}: {data[age_field]}'
                )

        for url_field in ['nonspec_url', 'instruction_url']:
            if data.get(url_field) is not None:
                assert isinstance(data[url_field], str), (
                    f'{url_field} должен быть строкой, получен {type(data[url_field])}: {data[url_field]}'
                )

        assert isinstance(data.get('infections', []), list)
        for infection in data.get('infections', []):
            assert isinstance(infection.get('id'), int), (
                f'id инфекции должен быть int, получен {type(infection.get("id"))}'
            )
            assert isinstance(infection.get('name'), str), (
                f'name инфекции должен быть строкой, получен {type(infection.get("name"))}'
            )

        valid_codes = [
            'intramuscularly',
            'subcutaneously',
            'cutaneously',
            'intradermally',
            'drops',
            'pills',
            'intranasally',
        ]
        assert isinstance(data.get('administration_methods', []), list), 'administration_methods должен быть списком'
        for method in data.get('administration_methods', []):
            assert 'code' in method, f'Ожидалось поле "code" в методе введения. Ключи: {list(method.keys())}'
            assert method['code'] in valid_codes, (
                f'Недопустимый код метода: {method.get("code")}. Допустимые: {valid_codes}'
            )
            assert 'age_group' in method, f'Ожидалось поле "age_group" в методе введения. Ключи: {list(method.keys())}'
            assert method['age_group'] is None or isinstance(method['age_group'], str), (
                f'age_group должен быть строкой или null, получен {type(method["age_group"])}: {method["age_group"]}'
            )
            assert 'note' in method, f'Ожидалось поле "note" в методе введения. Ключи: {list(method.keys())}'
            assert method['note'] is None or isinstance(method['note'], str), (
                f'note должен быть строкой или null, получен {type(method["note"])}: {method["note"]}'
            )

        if data.get('comment') is not None:
            assert isinstance(data['comment'].get('source'), str), 'source комментария должен быть строкой'
            assert isinstance(data['comment'].get('text'), str), 'text комментария должен быть строкой'

        for field in [
            'manufacturer',
            'storage_conditions',
            'schedule_info',
            'side_effects',
            'indications',
        ]:
            if data.get(field) is not None:
                assert isinstance(data[field], str), (
                    f'{field} должен быть строкой, получен {type(data[field])}: {data[field]}'
                )

    def test_get_full_card_with_versions(self, api_client, sample_vaccine_card_with_versions):
        """Получение карточки с несколькими версиями."""
        vaccine_card, versions = sample_vaccine_card_with_versions
        url = reverse(self.URL_DETAIL, kwargs={'pk': vaccine_card.id})
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        assert data['name'] == versions[-1].name, (
            f'Ожидалось имя последней версии "{versions[-1].name}", получено "{data.get("name")}"'
        )

    def test_get_nonexistent_vaccine(self, api_client):
        """Запрос несуществующей вакцины."""
        url = reverse(self.URL_DETAIL, kwargs={'pk': 99999})
        response = api_client.get(url)
        assert response.status_code == 404, (
            f'Ожидался статус 404 для несуществующей вакцины, получен {response.status_code}. URL: {url}'
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
            f'Ожидался статус 404 или 403 для скрытой вакцины, получен {response.status_code}. URL: {url}'
        )

    def test_minimal_card(self, api_client, sample_vaccine_versions):
        """Получение минимальной карточки вакцины."""
        version = sample_vaccine_versions[1]
        url = reverse(self.URL_DETAIL, kwargs={'pk': version.vaccine_card.id})
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        assert data['name'] == version.name, f'Ожидалось name="{version.name}", получено "{data.get("name")}"'


class TestVaccinePdf:
    """Тесты для /vaccines/{id}/pdf — скачивание PDF."""

    def test_get_pdf_redirect(self, api_client, sample_vaccine_versions):
        """Успешное скачивание PDF — редирект на файл."""
        version = sample_vaccine_versions[0]
        url = reverse('vaccine-pdf', kwargs={'id': version.vaccine_card.id})

        response = api_client.get(url)
        assert response.status_code == 302, f'Ожидался статус 302 (редирект), получен {response.status_code}.'
        assert response.url == version.pdf_url, f"Ожидался редирект на '{version.pdf_url}', получен '{response.url}'."

    def test_get_pdf_not_found(self, api_client, sample_vaccine_versions):
        """PDF не найден — ссылка отсутствует."""
        version = sample_vaccine_versions[1]
        version.pdf_url = ''
        version.save()

        url = reverse('vaccine-pdf', kwargs={'id': version.vaccine_card.id})
        response = api_client.get(url)
        assert response.status_code == 404, f'Ожидался статус 404 для вакцины без PDF, получен {response.status_code}.'

    def test_get_pdf_nonexistent_vaccine(self, api_client):
        """PDF для несуществующей вакцины."""
        url = reverse('vaccine-pdf', kwargs={'id': 99999})
        response = api_client.get(url)
        assert response.status_code == 404, f'Ожидался статус 404, получен {response.status_code}.'


class TestVaccineOfficialLink:
    """Тесты для /vaccines/{id}/official-link — ссылка на ГРЛС."""

    def test_get_official_link(self, api_client, sample_vaccine_versions):
        """Получение ссылки на официальную инструкцию (ГРЛС)."""
        version = sample_vaccine_versions[0]
        url = reverse('official-link', kwargs={'id': version.vaccine_card.id})

        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert 'url' in data, f'Ожидалось поле "url" в ответе. Ключи: {list(data.keys())}'
        assert data['url'] == version.ohlp_url, f"Ожидался url '{version.ohlp_url}', получен '{data.get('url')}'."

    def test_get_official_link_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на ГРЛС."""
        version = sample_vaccine_versions[1]
        version.ohlp_url = ''
        version.save()

        url = reverse('official-link', kwargs={'id': version.vaccine_card.id})
        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert data['url'] == '', f"Ожидалась пустая строка, получено '{data.get('url')}'."

    def test_get_official_link_nonexistent_vaccine(self, api_client):
        """Ссылка для несуществующей вакцины."""
        url = reverse('official-link', kwargs={'id': 99999})
        response = api_client.get(url)
        assert response.status_code == 404, f'Ожидался статус 404, получен {response.status_code}.'


class TestVaccineInstructionPatient:
    """Тесты для /vaccines/{id}/instruction-patient — инструкция для неспециалистов."""

    def test_get_instruction_patient(self, api_client, sample_vaccine_versions):
        """Получение ссылки на инструкцию для неспециалистов."""
        version = sample_vaccine_versions[0]
        url = reverse('instruction-patient', kwargs={'id': version.vaccine_card.id})

        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert 'url' in data, f'Ожидалось поле "url" в ответе. Ключи: {list(data.keys())}'
        assert data['url'] == version.nonspec_url, f"Ожидался url '{version.nonspec_url}', получен '{data.get('url')}'."

    def test_get_instruction_patient_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на инструкцию для неспециалистов."""
        version = sample_vaccine_versions[1]
        version.nonspec_url = ''
        version.save()

        url = reverse('instruction-patient', kwargs={'id': version.vaccine_card.id})
        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert data['url'] == '', f"Ожидалась пустая строка, получено '{data.get('url')}'."

    def test_get_instruction_patient_nonexistent_vaccine(self, api_client):
        """Инструкция для несуществующей вакцины."""
        url = reverse('instruction-patient', kwargs={'id': 99999})
        response = api_client.get(url)
        assert response.status_code == 404, f'Ожидался статус 404, получен {response.status_code}.'


class TestVaccineInstructionSpecialist:
    """Тесты для /vaccines/{id}/instruction-specialist — инструкция для специалистов."""

    def test_get_instruction_specialist(self, api_client, sample_vaccine_versions):
        """Получение ссылки на инструкцию для специалистов."""
        version = sample_vaccine_versions[0]
        url = reverse('instruction-specialist', kwargs={'id': version.vaccine_card.id})

        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert 'url' in data, f'Ожидалось поле "url" в ответе. Ключи: {list(data.keys())}'
        assert data['url'] == version.instruction_url, (
            f"Ожидался url '{version.instruction_url}', получен '{data.get('url')}'."
        )

    def test_get_instruction_specialist_empty(self, api_client, sample_vaccine_versions):
        """Пустая ссылка на инструкцию для специалистов."""
        version = sample_vaccine_versions[1]
        version.instruction_url = ''
        version.save()

        url = reverse('instruction-specialist', kwargs={'id': version.vaccine_card.id})
        response = api_client.get(url)
        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()
        assert data['url'] == '', f"Ожидалась пустая строка, получено '{data.get('url')}'."

    def test_get_instruction_specialist_nonexistent_vaccine(self, api_client):
        """Инструкция для несуществующей вакцины."""
        url = reverse('instruction-specialist', kwargs={'id': 99999})
        response = api_client.get(url)
        assert response.status_code == 404, f'Ожидался статус 404, получен {response.status_code}.'
