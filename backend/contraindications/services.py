from django.db.models import DecimalField, ExpressionWrapper, F, Prefetch
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from contraindications.models import Contraindication
from vaccines.models import (
    VaccineCard,
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
)


def get_vaccines_by_contraindication(contraindication_id: int) -> list[dict]:
    """Возвращает опубликованные видимые вакцины, связанные с противопоказанием."""
    version_ids = VaccineCardVersionContraindication.objects.filter(
        contraindication_id=contraindication_id,
    ).values('vaccine_card_version_id')
    vaccines = (
        VaccineCard.objects.filter(
            is_visible=True,
            published_version_id__in=version_ids,
        )
        .select_related('published_version')
        .prefetch_related(
            Prefetch(
                'published_version__contraindications_relations',
                queryset=VaccineCardVersionContraindication.objects.select_related(
                    'contraindication',
                ),
            ),
            Prefetch(
                'published_version__administration_method_relations',
                queryset=VaccineCardVersionAdministrationMethod.objects.select_related(
                    'administration_method',
                ),
            ),
        )
        .order_by('published_version__name', 'id')
    )

    return [_serialize_vaccine_card(vaccine) for vaccine in vaccines]


def _serialize_vaccine_card(vaccine: VaccineCard) -> dict:
    """Преобразует карточку вакцины в краткий публичный формат."""
    version = vaccine.published_version
    contraindications = [
        {
            'id': relation.contraindication.id,
            'name': relation.contraindication.name,
            'type': relation.contraindication_type,
        }
        for relation in version.contraindications_relations.all()
    ]
    administration_methods = [
        {
            'id': relation.administration_method.id,
            'name': relation.administration_method.name,
            'ageGroup': relation.age_group,
            'note': relation.note,
        }
        for relation in version.administration_method_relations.all()
    ]

    return {
        'id': vaccine.id,
        'name': version.name,
        'officialName': version.official_name,
        'minAge': version.min_age_months,
        'maxAge': version.max_age_months,
        'pregnancyUsageStatus': version.pregnancy_usage_status,
        'contraindications': contraindications,
        'administrationMethods': administration_methods,
    }


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
