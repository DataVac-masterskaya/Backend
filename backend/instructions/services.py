from django.db.models import DecimalField, ExpressionWrapper, F
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from instructions.models import OfficialInstruction
from vaccines.models import VaccineCard


def get_vaccines_by_official_instruction(instruction_id: int) -> list[dict]:
    """Возвращает опубликованные вакцины, связанные с официальной инструкцией."""
    vaccine_cards = (
        VaccineCard.objects.filter(
            is_visible=True,
            published_version__official_instruction_id=instruction_id,
        )
        .select_related('published_version')
        .order_by('published_version__name', 'id')
    )

    return [
        {
            'id': vaccine_card.id,
            'name': vaccine_card.published_version.name,
            'officialName': vaccine_card.published_version.official_name,
            'manufacturer': vaccine_card.published_version.manufacturer,
        }
        for vaccine_card in vaccine_cards
    ]


def search_official_instructions(query: str, limit: int = 6):
    """Ищет официальные инструкции по названию и поисковому весу."""
    queryset = OfficialInstruction.objects.all()
    normalized_query = query.strip()

    if normalized_query:
        queryset = queryset.filter(title__icontains=normalized_query)

    search_score = ExpressionWrapper(
        F('search_weight') + F('search_select_count'),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )

    return queryset.annotate(
        search_score=search_score,
        lower_title=Lower('title'),
    ).order_by('-search_score', 'lower_title')[:limit]


def increment_official_instruction_select_count(
    instruction_id: int,
) -> OfficialInstruction:
    """Увеличивает счетчик выбора официальной инструкции."""
    OfficialInstruction.objects.filter(id=instruction_id).update(
        search_select_count=F('search_select_count') + 1,
    )
    return get_object_or_404(OfficialInstruction, id=instruction_id)
