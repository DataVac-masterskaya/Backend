from contraindications.services import increment_contraindication_select_count, search_contraindications
from django.db.models import DecimalField, ExpressionWrapper, F, QuerySet
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from instructions.services import increment_official_instruction_select_count, search_official_instructions
from reference_books.models import Infection, Ingredients

SUGGESTIONS_LIMIT = 6


def _search_by_name(
    queryset: QuerySet,
    query: str,
    limit: int = SUGGESTIONS_LIMIT,
) -> QuerySet:
    """Ищет сущности с полем name по правилам сортировки подсказок."""
    normalized_query = query.strip()

    if normalized_query:
        queryset = queryset.filter(name__icontains=normalized_query)

    search_score = ExpressionWrapper(
        F('search_weight') + F('search_select_count'),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )

    return queryset.annotate(
        search_score=search_score,
        lower_name=Lower('name'),
    ).order_by('-search_score', 'lower_name')[:limit]


def search_infections(query: str, limit: int = SUGGESTIONS_LIMIT) -> QuerySet:
    """Ищет инфекции по названию для глобальных поисковых подсказок."""
    return _search_by_name(Infection.objects.all(), query, limit)


def search_ingredients(query: str, limit: int = SUGGESTIONS_LIMIT) -> QuerySet:
    """Ищет ингредиенты по названию для глобальных поисковых подсказок."""
    return _search_by_name(Ingredients.objects.all(), query, limit)


def _serialize_name_suggestions(items: QuerySet) -> list[dict]:
    """Приводит сущности с полем name к единому формату поисковой подсказки."""
    return [
        {
            'id': item.id,
            'name': item.name,
            'score': item.search_score,
        }
        for item in items
    ]


def _serialize_instruction_suggestions(items: QuerySet) -> list[dict]:
    """Приводит официальные инструкции к единому формату подсказки."""
    return [
        {
            'id': item.id,
            'name': item.title,
            'score': item.search_score,
        }
        for item in items
    ]


def get_search_suggestions(
    query: str,
    limit: int = SUGGESTIONS_LIMIT,
) -> dict[str, list[dict]]:
    """
    Возвращает поисковые подсказки, сгруппированные по сущностям DataVac.

    TODO: Подключить группу vaccines после реализации публичных моделей
    и правил видимости опубликованных версий.
    """
    return {
        'contraindications': _serialize_name_suggestions(
            search_contraindications(query, limit),
        ),
        'infections': _serialize_name_suggestions(
            search_infections(query, limit),
        ),
        'ingredients': _serialize_name_suggestions(
            search_ingredients(query, limit),
        ),
        'instructions': _serialize_instruction_suggestions(
            search_official_instructions(query, limit),
        ),
    }


def increment_infection_select_count(infection_id: int) -> Infection:
    """Увеличивает счетчик выбора поисковой подсказки для инфекции."""
    Infection.objects.filter(id=infection_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(Infection, id=infection_id)


def increment_ingredient_select_count(ingredient_id: int) -> Ingredients:
    """Увеличивает счетчик выбора поисковой подсказки для ингредиента."""
    Ingredients.objects.filter(id=ingredient_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(Ingredients, id=ingredient_id)


def select_search_suggestion(entity_type: str, entity_id: int):
    """Фиксирует выбор поисковой подсказки и возвращает обновленную сущность."""
    handlers = {
        'contraindication': increment_contraindication_select_count,
        'infection': increment_infection_select_count,
        'ingredient': increment_ingredient_select_count,
        'instruction': increment_official_instruction_select_count,
    }
    return handlers[entity_type](entity_id)
