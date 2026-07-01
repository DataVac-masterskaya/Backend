from functools import partial

from datavac.utils import increment_select_count
from django_filters.rest_framework import DjangoFilterBackend
from instructions.models import OfficialInstruction
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from contraindications.models import Contraindication
from reference_books.models import Infection, Ingredients, MethodsOfAdministration
from vaccines.models import VaccineCard

from .filters import InfectionFilter, OrderingFilterSortBy
from .serializers import (
    InfectionCartSerializer,
    InfectionSerializer,
    IngredientsSerializer,
    MethodsOfAdministrationCartSerializer,
    MethodsOfAdministrationSerializer,
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


class MethodsOfAdministrationViewSet(viewsets.ReadOnlyModelViewSet):
    """Cпособы введения."""

    queryset = MethodsOfAdministration.objects.all()

    def get_serializer_class(self):
        """Выбирает сериализатор."""
        if self.action == 'retrieve':
            return MethodsOfAdministrationCartSerializer
        return MethodsOfAdministrationSerializer


class SearchSelectView(APIView):
    """Фиксирует выбор сущности в поисковой подсказке."""

    SERVICE_MAP = {
        'infection': partial(increment_select_count, Infection),
        'ingredient': partial(increment_select_count, Ingredients),
        'contraindication': partial(increment_select_count, Contraindication),
        'instruction': partial(increment_select_count, OfficialInstruction),
        'vaccineCard': partial(increment_select_count, VaccineCard),
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
