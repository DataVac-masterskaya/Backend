from urllib.parse import urlencode

import pytest
from django.urls import reverse
from utils import get_count, get_results

pytestmark = pytest.mark.django_db


class TestIngredients:
    """Тесты для /ingredients."""

    URL_LIST = 'ingredients-list'

    VALID_TYPES = [
        'Адъювант',
        'Стабилизатор',
        'Консервант',
        'Подсластитель',
        'Эмульгатор',
        'Следы производства',
    ]

    def test_list_ingredients(self, api_client, sample_ingredients):
        """Получение списка ингредиентов с проверкой структуры."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        count = get_count(data, results)
        assert count == len(sample_ingredients), (
            f'Ожидалось {len(sample_ingredients)} ингредиентов, получено {count}. Данные: {data}'
        )
        assert len(results) > 0, f'Список ингредиентов пуст, но в фикстуре создано {len(sample_ingredients)} записей.'

        item = results[0]

        assert 'id' in item, f'Ожидалось поле "id" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['id'], int), (
            f'Поле "id" должно быть целым числом, получен тип {type(item["id"])}. Значение: {item["id"]}'
        )
        assert 'name' in item, f'Ожидалось поле "name" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['name'], str) and len(item['name']) > 0, (
            f'Поле "name" должно быть непустой строкой, получен тип {type(item["name"])}. Значение: {item["name"]}'
        )
        assert 'type' in item, f'Ожидалось поле "type" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['type'], str), (
            f'Поле "type" должно быть строкой, получен тип {type(item["type"])}. Значение: {item["type"]}'
        )
        assert item['type'] in self.VALID_TYPES, (
            f"Недопустимый тип ингредиента: '{item['type']}'. Допустимые типы: {self.VALID_TYPES}"
        )
        assert 'popularity' in item, f'Ожидалось поле "popularity" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['popularity'], int), (
            f'Поле "popularity" должно быть целым числом, получен тип {type(item["popularity"])}. '
            f'Значение: {item["popularity"]}'
        )

    def test_valid_types(self, api_client, sample_ingredients):
        """Проверка, что все типы ингредиентов в ответе — из допустимого списка."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, 'Список ингредиентов пуст, невозможно проверить типы.'

        invalid_types = []
        for item in results:
            if item['type'] not in self.VALID_TYPES:
                invalid_types.append({'name': item.get('name'), 'type': item.get('type')})

        assert not invalid_types, (
            f'Найдены ингредиенты с недопустимыми типами: {invalid_types}. '
            f'Допустимые типы: {self.VALID_TYPES}. '
            f'Все типы в ответе: {[item["type"] for item in results]}'
        )

    def test_filter_by_type(self, api_client, sample_ingredients):
        """Фильтрация по типу ингредиента."""
        url = reverse(self.URL_LIST)
        params = {'type': self.VALID_TYPES[0]}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        for item in results:
            assert item['type'] == self.VALID_TYPES[0], (
                f"Ожидался тип '{self.VALID_TYPES[0]}', "
                f"получен '{item['type']}' для ингредиента '{item.get('name')}'. "
                f'Параметры запроса: {params}'
            )

    def test_filter_by_invalid_type(self, api_client):
        """Фильтрация по несуществующему типу."""
        url = reverse(self.URL_LIST)
        params = {'type': 'НесуществующийТип'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f"Ожидался пустой список для несуществующего типа '{params['type']}', "
            f'но получено {len(results)} записей. Данные: {results}'
        )

    def test_sort_by_name(self, api_client, sample_ingredients):
        """Сортировка по названию (по умолчанию)."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names), f'Сортировка по названию нарушена. Ожидалось: {sorted(names)}, получено: {names}'

    def test_sort_by_name_desc(self, api_client, sample_ingredients):
        """Сортировка по названию в обратном порядке."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'name_desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names, reverse=True), (
            f'Обратная сортировка по названию нарушена. Ожидалось: {sorted(names, reverse=True)}, получено: {names}'
        )

    def test_sort_by_type(self, api_client, sample_ingredients):
        """Сортировка по типу ингредиента."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'type'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        types = [item['type'] for item in results]
        assert types == sorted(types), f'Сортировка по типу нарушена. Ожидалось: {sorted(types)}, получено: {types}'

    def test_sort_by_type_desc(self, api_client, sample_ingredients):
        """Сортировка по типу в обратном порядке."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'type_desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        types = [item['type'] for item in results]
        assert types == sorted(types, reverse=True), (
            f'Обратная сортировка по типу нарушена. Ожидалось: {sorted(types, reverse=True)}, получено: {types}'
        )

    def test_sort_by_popularity(self, api_client, sample_ingredients):
        """Сортировка по популярности (от большего к меньшему)."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'popularity'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        if len(results) > 1:
            popularity_values = [item['popularity'] for item in results]
            assert popularity_values == sorted(popularity_values, reverse=True), (
                f'Сортировка по популярности (DESC) нарушена. '
                f'Ожидалось: {sorted(popularity_values, reverse=True)}, '
                f'получено: {popularity_values}'
            )

    def test_search_by_q(self, api_client, sample_ingredients):
        """Поиск по названию через параметр q."""
        url = reverse(self.URL_LIST)

        params = {'q': 'Алюминия'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, (
            f"Поиск по '{params['q']}' не вернул результатов. Ожидался хотя бы 1 ингредиент. Данные: {data}"
        )
        for item in results:
            assert 'Алюминия' in item['name'], (
                f"Ингредиент '{item['name']}' не содержит 'Алюминия'. Параметры поиска: {params}"
            )

        params = {'q': 'НесуществующийИнгредиент'}
        response = api_client.get(f'{url}?{urlencode(params)}')
        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f"Поиск по '{params['q']}' должен вернуть пустой список, "
            f'но получено {len(results)} записей. Данные: {results}'
        )

    def test_pagination(self, api_client, sample_ingredients):
        """Пагинация через limit."""
        url = reverse(self.URL_LIST)
        params = {'limit': 2}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        count = get_count(data, results)
        assert len(results) == 2, (
            f'Ожидалось 2 элемента на странице (limit=2), получено {len(results)}. Данные: {results}'
        )
        assert count == len(sample_ingredients), (
            f'Общее количество записей не совпадает с фикстурой. Ожидалось {len(sample_ingredients)}, получено {count}.'
        )
