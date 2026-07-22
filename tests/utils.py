def get_results(data):
    """Извлекает список результатов из ответа API.

    Поддерживает два формата ответа:
    - Список: [{...}, {...}]
    - Пагинированный словарь: {"count": N, "results": [{...}, {...}]}

    Args:
        data: ответ API, распарсенный из JSON.

    Returns:
        list: список элементов.

    Raises:
        AssertionError: если формат ответа не поддерживается.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and 'results' in data:
        return data['results']
    raise AssertionError(
        f'Неожиданный формат ответа: {type(data)}. Ключи: {list(data.keys()) if isinstance(data, dict) else "N/A"}'
    )


def get_count(data, results):
    """Извлекает общее количество записей из ответа API.

    Если ответ пагинированный — берёт count из словаря.
    Если ответ — список, возвращает длину списка.

    Args:
        data: ответ API, распарсенный из JSON.
        results: список элементов, извлечённый через get_results().

    Returns:
        int: общее количество записей.
    """
    if isinstance(data, dict) and 'count' in data:
        return data['count']
    return len(results)
