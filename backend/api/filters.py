from django_filters import rest_framework
from reference_books.models import Category, Infection
from rest_framework.filters import OrderingFilter


class InfectionFilter(rest_framework.FilterSet):
    category = rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='category__name',
        to_field_name='name',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Infection
        fields = [
            'category',
        ]


class OrderingFilterSortBy(OrderingFilter):
    ordering_param = 'sort_by'

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            # Заменяем category на category__name для сортировки по названию.
            ordering_fields = []
            for field in ordering:
                if field == 'category':
                    ordering_fields.append('category__name')
                elif field == '-category':
                    ordering_fields.append('-category__name')
                else:
                    ordering_fields.append(field)
            return queryset.order_by(*ordering_fields)

        return queryset
