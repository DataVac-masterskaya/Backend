from django.db.models import F, Model
from django.shortcuts import get_object_or_404


def increment_select_count(model: type[Model], entity_id: int) -> Model:
    """Увеличивает счётчик выбора поисковой подсказки для любой сущности."""
    model.objects.filter(id=entity_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(model, id=entity_id)
