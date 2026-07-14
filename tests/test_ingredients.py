from urllib.parse import urlencode

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestIngredients:
    """Тесты для /ingredients/"""

    URL_LIST = 'ingredients-list'

    def test_list_ingredients(self, api_client, sample_ingredients):
        """Получение списка ингредиентов."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        assert len(data) == len(sample_ingredients), (
            f'Ожидалось {len(sample_ingredients)} ингредиентов, получено {len(data)}. Данные: {data}'
        )

    def test_filter_by_type(self, api_client, sample_ingredients):
        """Фильтрация по типу ингредиента."""
        url = reverse(self.URL_LIST)
        params = {'type': 'Действующее вещество'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) > 0, (
            f"Ожидался хотя бы 1 ингредиент с типом 'Действующее вещество', "
            f'получено {len(data)} результатов. Данные: {data}'
        )
        for item in data:
            assert item['type'] == 'Действующее вещество', (
                f"Ожидался тип 'Действующее вещество', получен '{item['type']}'. Данные элемента: {item}"
            )

    def test_filter_by_type_case_insensitive(self, api_client, sample_ingredients):
        """Регистронезависимый поиск по типу (если поддерживается)."""
        url = reverse(self.URL_LIST)
        params = {'type': 'действующее вещество'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        if len(data) > 0:
            for item in data:
                assert 'действующее' in item['type'].lower(), (
                    f"Ожидался тип, содержащий 'действующее' "
                    f'(регистронезависимо), '
                    f"получен '{item['type']}'. Данные элемента: {item}"
                )

    def test_sort_by_name_asc(self, api_client, sample_ingredients):
        """Сортировка по name asc."""
        url = reverse(self.URL_LIST)
        params = {'ordering': 'name'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f'Сортировка по возрастанию не работает. Ожидалось: {expected}, получено: {names}. Параметры: {params}'
        )

    def test_sort_by_name_desc(self, api_client, sample_ingredients):
        """Сортировка по name desc."""
        url = reverse(self.URL_LIST)
        params = {'ordering': '-name'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names, reverse=True)
        assert names == expected, (
            f'Сортировка по убыванию не работает. Ожидалось: {expected}, получено: {names}. Параметры: {params}'
        )

    def test_sort_by_type(self, api_client, sample_ingredients):
        """Сортировка по type."""
        url = reverse(self.URL_LIST)
        params = {'ordering': 'type'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        types = [item['type'] for item in data]
        expected = sorted(types)
        assert types == expected, (
            f'Сортировка по типу (возрастание) не работает. '
            f'Ожидалось: {expected}, получено: {types}. '
            f'Параметры: {params}'
        )

    def test_sort_by_type_desc(self, api_client, sample_ingredients):
        """Сортировка по type desc."""
        url = reverse(self.URL_LIST)
        params = {'ordering': '-type'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        types = [item['type'] for item in data]
        expected = sorted(types, reverse=True)
        assert types == expected, (
            f'Сортировка по типу (убывание) не работает. Ожидалось: {expected}, получено: {types}. Параметры: {params}'
        )

    def test_combined_filter_and_sort(self, api_client, sample_ingredients):
        """Комбинация фильтрации и сортировки."""
        url = reverse(self.URL_LIST)
        params = {'type': 'Действующее вещество', 'ordering': 'name'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        for item in data:
            assert item['type'] == 'Действующее вещество', (
                f'Фильтрация нарушена при комбинированном запросе. '
                f"Ожидался тип 'Действующее вещество', получен "
                f"'{item['type']}'. "
                f'Данные: {item}, params: {params}'
            )
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f'Сортировка нарушена при комбинированном запросе. '
            f'Ожидалось: {expected}, получено: {names}. '
            f'params: {params}'
        )

    def test_nonexistent_type(self, api_client):
        """Несуществующий тип ингредиента."""
        url = reverse(self.URL_LIST)
        params = {'type': 'Несуществующий тип'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) == 0, (
            f'Ожидался пустой список для несуществующего типа '
            f"'Несуществующий тип', получено {len(data)} записей. "
            f'Данные: {data}'
        )
