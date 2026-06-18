from django.db.models import F
from django.shortcuts import get_object_or_404

from reference_books.models import Infection, Ingredients


def increment_infection_select_count(infection_id: int) -> Infection:
    """Увеличивает счётчик выбора поисковой подсказки для инфекции."""
    Infection.objects.filter(id=infection_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(Infection, id=infection_id)


def increment_ingredients_select_count(ingredient_id: int) -> Ingredients:
    """Увеличивает счётчик выбора поисковой подсказки для ингредиента."""
    Ingredients.objects.filter(id=ingredient_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(Ingredients, id=ingredient_id)
