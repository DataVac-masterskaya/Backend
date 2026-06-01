from django.db.models import DecimalField, ExpressionWrapper, F
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from contraindications.models import Contraindication


def get_vaccines_by_contraindication(contraindication_id: int) -> list[dict]:
    """
    Возвращает вакцины, связанные с противопоказанием.

    TODO: Подключить модуль карточек вакцин после того, как
    реализуются модели VaccineCard/VaccineCardVersion.
    """
    return []


def search_contraindications(query: str, limit: int = 6):
    """Ищет противопоказания по названию и поисковому весу."""
    queryset = Contraindication.objects.all()
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


def increment_contraindication_select_count(
    contraindication_id: int,
) -> Contraindication:
    """Увеличивает счетчик выбора поисковой подсказки для противопоказания."""
    Contraindication.objects.filter(id=contraindication_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(Contraindication, id=contraindication_id)
