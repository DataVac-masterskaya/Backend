from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from contraindications.models import Contraindication, ContraindicationCategory
from contraindications.serializers import (
    ContraindicationCategorySerializer,
    ContraindicationDetailSerializer,
    ContraindicationFrontendListSerializer,
    ContraindicationListSerializer,
    ContraindicationSearchSerializer,
    ContraindicationVaccinesResponseSerializer,
    SelectCounterResponseSerializer,
)
from contraindications.services import (
    get_vaccines_by_contraindication,
    increment_contraindication_select_count,
    search_contraindications,
)


class ContraindicationCategoryListView(APIView):
    """Отдает список категорий противопоказаний."""

    @extend_schema(responses=ContraindicationCategorySerializer(many=True))
    def get(self, request):
        """Возвращает категории противопоказаний в алфавитном порядке."""
        categories = ContraindicationCategory.objects.order_by('name')
        serializer = ContraindicationCategorySerializer(categories, many=True)
        return Response(serializer.data)


class ContraindicationListView(APIView):
    """Отдает список противопоказаний по контракту фронтенда."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                description='Название категории противопоказаний.',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='sort',
                description='Сортировка списка: popularity или name.',
                required=False,
                type=str,
                enum=['popularity', 'name'],
            ),
        ],
        responses=ContraindicationFrontendListSerializer(many=True),
    )
    def get(self, request):
        """Возвращает список с основной категорией и популярностью."""
        contraindications = Contraindication.objects.prefetch_related(
            'categories',
        ).order_by('name')
        category = request.query_params.get('category')
        sort = request.query_params.get('sort', 'name')

        if category:
            contraindications = contraindications.filter(
                categories__name=category.strip(),
            )

        if sort not in {'popularity', 'name'}:
            return Response(
                {'detail': 'sort must be one of: popularity, name.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sort == 'popularity':
            contraindications = contraindications.order_by(
                '-search_select_count',
                'name',
            )

        serializer = ContraindicationFrontendListSerializer(
            contraindications.distinct(),
            many=True,
        )
        return Response(serializer.data)


class ContraindicationLegacyListView(APIView):
    """Отдает список противопоказаний по прежнему контракту."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='categoryId',
                description='ID категории противопоказаний.',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name='search',
                description='Поиск по названию противопоказания.',
                required=False,
                type=str,
            ),
        ],
        responses=ContraindicationListSerializer(many=True),
        deprecated=True,
    )
    def get(self, request):
        """Возвращает прежний список с фильтрацией и поиском."""
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

    @extend_schema(responses=ContraindicationDetailSerializer)
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

    @extend_schema(responses=ContraindicationVaccinesResponseSerializer)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Поисковая строка.',
                required=False,
                type=str,
            ),
        ],
        responses=ContraindicationSearchSerializer(many=True),
    )
    def get(self, request):
        """Возвращает до шести подсказок по поисковой строке."""
        query = request.query_params.get('q', '')
        serializer = ContraindicationSearchSerializer(
            search_contraindications(query),
            many=True,
        )
        return Response(serializer.data)


class SelectContraindicationView(APIView):
    """Фиксирует выбор противопоказания в поисковой подсказке."""

    @extend_schema(request=None, responses=SelectCounterResponseSerializer)
    def post(self, request, pk: int):
        """Увеличивает счетчик выбора противопоказания."""
        contraindication = increment_contraindication_select_count(pk)
        return Response(
            {
                'id': contraindication.id,
                'searchSelectCount': contraindication.search_select_count,
            },
        )
