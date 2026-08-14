from django.db.models import Q
from django_filters import CharFilter, ChoiceFilter, FilterSet
from rest_framework.exceptions import ValidationError

from vaccines.models import VaccineCard

CHOICE_FOR_FILTER = [('infection', 'infection'), ('ingredient', 'ingredient'), ('contraindication', 'contraindication')]


class VaccineFilter(FilterSet):
    """Фильтры для списка вакцин."""

    first_letter = CharFilter(
        method='filter_by_first_letter',
    )
    filter_type = ChoiceFilter(
        choices=CHOICE_FOR_FILTER,
        method='filter_by_entity',
    )
    search = CharFilter(
        method='filter_by_search',
    )

    class Meta:
        model = VaccineCard
        fields = []

    def filter_by_first_letter(self, queryset, name, value):
        """Фильтрация по первой букве названия (name или code_name)."""
        if value and len(value) == 1:
            return queryset.filter(
                Q(current_version__name__istartswith=value) | Q(current_version__code_name__istartswith=value)
            )
        return queryset

    def filter_by_entity(self, queryset, name, value):
        """Фильтрация по типу связанной сущности."""
        filter_id = self.data.get('filter_id')

        if not filter_id:
            return queryset
        try:
            filter_id = int(filter_id)
        except (TypeError, ValueError):
            raise ValidationError({'filter_id': 'Должно быть целым числом.'})

        if value == 'infection':
            return queryset.filter(current_version__infections__id=filter_id)
        if value == 'ingredient':
            return queryset.filter(current_version__ingredients__id=filter_id)
        if value == 'contraindication':
            return queryset.filter(current_version__contraindications__id=filter_id)
        return queryset

    def filter_by_search(self, queryset, name, value):
        """Поиск вакцины по названию (name или official_name)."""
        if not value:
            return queryset
        return queryset.filter(
            Q(current_version__name__icontains=value) | Q(current_version__official_name__icontains=value)
        )
