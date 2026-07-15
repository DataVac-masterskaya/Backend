from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, status

from vaccines.constants import VACCINE_TAG
from vaccines.filters import VaccineFilter
from vaccines.models import VaccineCard
from vaccines.pagination import StandardPagination
from vaccines.serializers.publush_serializers import VaccineCardDetail, VaccineCardShort


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Список вакцин',
    description='Возвращает список вакцин с поддержкой сортировки, фильтрации по первой букве и связанной сущности.',
    parameters=[
        OpenApiParameter(
            name='ordering',
            type=str,
            enum=[
                'current_version__name',
                '-current_version__name',
                'current_version__official_name',
                '-current_version__official_name',
            ],
            description=(
                'Поле сортировки. Добавьте `-` для сортировки по убыванию.\n'
                'Примеры: `ordering=current_version__name` (по названию, от А до Я), '
                '`ordering=-current_version__official_name` (по офиц. названию, от Я до А)'
            ),
        ),
        OpenApiParameter(
            name='first_letter',
            type=str,
            description='Фильтр по первой букве названия. Пример: `first_letter=А`',
        ),
        OpenApiParameter(
            name='filter_type',
            type=str,
            enum=['infection', 'ingredient', 'contraindication'],
            description='Тип связанной сущности для фильтрации',
        ),
        OpenApiParameter(
            name='filter_id',
            type=int,
            description='ID связанной сущности (используется вместе с filter_type)',
        ),
    ],
    responses={
        status.HTTP_200_OK: VaccineCardShort(many=True),
    },
)
class PublishVaccinesViews(generics.ListAPIView):
    """Публичный эндпоинт списока вакцин с поддержкой сортировки, фильтрации."""

    serializer_class = VaccineCardShort
    filterset_class = VaccineFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['current_version__name', 'current_version__official_name']
    ordering = ['current_version__name']
    pagination_class = StandardPagination

    def get_queryset(self):
        return VaccineCard.objects.filter(is_visible=True, status='active').select_related('current_version')


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Детальная карточка вакцины',
    description='Возвращает полную информацию о вакцине по ID.',
    responses={status.HTTP_200_OK: VaccineCardDetail},
)
class PublicVaccineDetailView(generics.RetrieveAPIView):
    """Публичный эндпоинт детальная карточка вакцины."""

    serializer_class = VaccineCardDetail

    def get_queryset(self):
        return VaccineCard.objects.filter(is_visible=True, status='active').select_related('current_version')
