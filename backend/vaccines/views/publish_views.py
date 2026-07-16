from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, status
from rest_framework.views import APIView, Response

from vaccines.constants import VACCINE_TAG
from vaccines.filters import VaccineFilter
from vaccines.models import VaccineCard, VaccineCardStatus
from vaccines.pagination import StandardPagination
from vaccines.serializers.publush_serializers import VaccineCardDetail, VaccineCardShort


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Список вакцин',
    description='Возвращает список вакцин с поддержкой сортировки, пагинации, \n'
    'фильтрации, по первой букве и связанной сущности.',
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
    """Публичный эндпоинт списока вакцин с поддержкой сортировки, фильтрации и пагинации."""

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


class BaseVaccineLinkView(APIView):
    """Базовый класс для получения ссылок из карточки вакцины."""

    field_name = None
    redirect = False
    error_message = 'Ссылка не найдена.'

    def get(self, request, id):
        vaccine = get_object_or_404(
            VaccineCard.objects.select_related('current_version'),
            id=id,
            is_visible=True,
            status=VaccineCardStatus.ACTIVE,
        )
        if not vaccine.current_version:
            return Response({'detail': 'Не удалось найти версию вакцины.'}, status=status.HTTP_404_NOT_FOUND)
        url = getattr(vaccine.current_version, self.field_name, None)
        if not url:
            return Response({'detail': self.error_message}, status=status.HTTP_404_NOT_FOUND)
        if self.redirect:
            return HttpResponseRedirect(url)
        return Response({'url': url})


@extend_schema(
    tags=[VACCINE_TAG],
    summary='PDF-файл карточки вакцины',
    description='Перенаправляет на PDF-файл по ID карточки вакцины',
)
class VaccinePDFView(BaseVaccineLinkView):
    """Перенаправляет на PDF-файл карточки вакцины."""

    field_name = 'pdf_url'
    redirect = True
    error_message = 'PDF у карточки не найден.'


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Официальная инструкция',
    description='Возвращает ссылку на официальную инструкцию по ID карточки вакцины',
)
class VaccineInstructionView(BaseVaccineLinkView):
    """Возвращает ссылку на официальную инструкцию."""

    field_name = 'instruction_url'
    error_message = 'Ссылка на инструкцию не найдена.'


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Инструкция для пациентов',
    description='Возвращает ссылку на инструкцию для пациентов по ID карточки вакцины',
)
class VaccineInstructionPatientView(BaseVaccineLinkView):
    """Возвращает ссылку на инструкцию для пациентов."""

    field_name = 'nonspec_url'
    error_message = 'Ссылка на инструкцию для пациента не найдена.'


@extend_schema(
    tags=[VACCINE_TAG],
    summary='Инструкцию для специалистов',
    description='Возвращает ссылку на инструкцию для специалистов по ID карточки вакцины',
)
class VaccineInstructionSpecialistView(BaseVaccineLinkView):
    """Возвращает ссылку на инструкцию для специалистов."""

    field_name = 'ohlp_url'
    error_message = 'Ссылка на инструкцию для специалистов не найдена.'
