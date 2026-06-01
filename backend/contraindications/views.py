from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from contraindications.models import Contraindication, ContraindicationCategory
from contraindications.serializers import (
    ContraindicationCategorySerializer,
    ContraindicationDetailSerializer,
    ContraindicationListSerializer,
    ContraindicationSearchSerializer,
)
from contraindications.services import (
    get_vaccines_by_contraindication,
    increment_contraindication_select_count,
    search_contraindications,
)


class ContraindicationCategoryListView(APIView):
    """Отдает список категорий противопоказаний."""

    def get(self, request):
        """Возвращает категории противопоказаний в алфавитном порядке."""
        categories = ContraindicationCategory.objects.order_by('name')
        serializer = ContraindicationCategorySerializer(categories, many=True)
        return Response(serializer.data)


class ContraindicationListView(APIView):
    """Отдает список противопоказаний с фильтрацией и поиском."""

    def get(self, request):
        """Возвращает список противопоказаний по query-параметрам."""
        contraindications = Contraindication.objects.prefetch_related(
            'categories',
        ).order_by('name')
        category_id = request.query_params.get('categoryId')
        search = request.query_params.get('search')

        if category_id:
            if not category_id.isdigit():
                return Response(
                    {'detail': 'categoryId must be an integer.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            contraindications = contraindications.filter(
                categories__id=category_id,
            )

        if search:
            contraindications = contraindications.filter(
                name__icontains=search.strip(),
            )

        serializer = ContraindicationListSerializer(
            contraindications.distinct(),
            many=True,
        )
        return Response(serializer.data)


class ContraindicationDetailView(APIView):
    """Отдает детальную информацию о противопоказании."""

    def get(self, request, pk: int):
        """Возвращает противопоказание, категории и связанные вакцины."""
        contraindication = get_object_or_404(
            Contraindication.objects.prefetch_related('categories'),
            id=pk,
        )
        serializer = ContraindicationDetailSerializer(contraindication)
        return Response(serializer.data)


class ContraindicationVaccinesView(APIView):
    """Отдает список вакцин по выбранному противопоказанию."""

    def get(self, request, pk: int):
        """Возвращает вакцины, связанные с противопоказанием."""
        contraindication = get_object_or_404(Contraindication, id=pk)
        return Response(
            {
                'contraindicationId': contraindication.id,
                'vaccines': get_vaccines_by_contraindication(
                    contraindication.id,
                ),
            },
        )


class ContraindicationSearchView(APIView):
    """Отдает поисковые подсказки по противопоказаниям."""

    def get(self, request):
        """Возвращает до шести подсказок по поисковой строке."""
        query = request.query_params.get('q', '')
        serializer = ContraindicationSearchSerializer(
            search_contraindications(query),
            many=True,
        )
        return Response(serializer.data)


@api_view(['POST'])
def select_contraindication(request, pk: int):
    """Фиксирует выбор противопоказания в поисковой подсказке."""
    contraindication = increment_contraindication_select_count(pk)
    return Response(
        {
            'id': contraindication.id,
            'searchSelectCount': contraindication.search_select_count,
        },
    )
