from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from contraindications.services import increment_contraindication_select_count
from instructions.services import increment_official_instruction_select_count
from reference_books.models import Infection, Ingredients
from reference_books.services import (
    increment_infection_select_count,
    increment_ingredients_select_count,
)
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import InfectionFilter, OrderingFilterSortBy
from .serializers import (
    InfectionCartSerializer,
    InfectionSerializer,
    IngredientsSerializer,
    SearchSelectSerializer,
)


class InfectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Инфекции."""

    queryset = Infection.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilterSortBy)
    filterset_class = InfectionFilter
    ordering_fields = ('name', 'category', 'search_weight')

    def get_serializer_class(self):
        """Выбирает сериализатор."""
        if self.action == 'retrieve':
            return InfectionCartSerializer
        return InfectionSerializer

    def retrieve(self, request, *args, **kwargs):
        """Показывает карточку инфекции."""
        instance = self.get_object()
        # Обновляем счётчик показов.
        Infection.objects.filter(id=instance.id).update(search_select_count=F('search_select_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'type': ['exact'],
    }
    search_fields = ('name',)

    def get_queryset(self):
        queryset = super().get_queryset()

        sort_by = self.request.query_params.get('sort_by')
        direction = self.request.query_params.get('direction', 'asc')

        if sort_by:
            if sort_by in ['name', 'id', 'type']:
                order = sort_by if direction == 'asc' else f'-{sort_by}'
                queryset = queryset.order_by(order)

        return queryset


class SearchSelectView(APIView):
    """Фиксирует выбор сущности в поисковой подсказке."""

    SERVICE_MAP = {
        'infection': increment_infection_select_count,
        'ingredient': increment_ingredients_select_count,
        'contraindication': increment_contraindication_select_count,
        'instruction': increment_official_instruction_select_count,
    }

    def post(self, request):
        """Увеличивает счётчик выбранной сущности по entityType и entityId."""
        serializer = SearchSelectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entity_type = serializer.validated_data['entityType']
        entity_id = serializer.validated_data['entityId']

        service = self.SERVICE_MAP.get(entity_type)
        if not service:
            return Response(
                {'error': f'Unknown entityType: {entity_type}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service(entity_id)
        return Response({'success': True}, status=status.HTTP_200_OK)
