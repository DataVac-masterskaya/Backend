from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from vaccines.constants import VACCINE_TAG
from vaccines.models import VaccineCard
from vaccines.serializers.admin_serializers import (
    AdminVaccineCreateResponseSerializer,
    AdminVaccinesCreatedSerializers,
    AdminVaccinesDetailSerializers,
)


class AdminVaccineCreateAPIView(APIView):
    """Эндпоинт для создания карточки вакцины."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=[VACCINE_TAG],
        summary='Создать карточку вакцины',
        description=(
            'Создает новую карточку вакцины и первую версию со статусом DRAFT.\n\n'
            'Доступ: только для администраторов.\n\n'
            'Ожидает полные данные о вакцине, включая связи с инфекциями, '
            'ингредиентами, противопоказаниями и методами введения.'
        ),
        request=AdminVaccinesCreatedSerializers,
        responses={
            status.HTTP_201_CREATED: AdminVaccineCreateResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Пример запроса.',
                value={
                    'name': 'Инфанрикс Гекса',
                    'official_name': 'Инфанрикс Гекса, суспензия',
                    'is_available_in_rf': 'true',
                    'infection_ids': [1, 2, 3],
                    'ingredients': [{'ingredient_id': 1, 'role': 'active'}],
                    'contraindications': [{'contraindication_id': 1, 'type': 'absolute'}],
                    'comment': {'source': 'АНО', 'text': 'Комментарий'},
                },
                request_only=True,
            ),
            OpenApiExample(
                'Пример успешного ответа',
                value={'id': 1, 'current_version_id': 1, 'status': 'draft'},
                response_only=True,
                status_codes=[status.HTTP_201_CREATED],
            ),
        ],
    )
    def post(self, request):
        serializer = AdminVaccinesCreatedSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        response_serializer = AdminVaccineCreateResponseSerializer(version.vaccine_card)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AdminVaccineDetailAPIView(APIView):
    """Эндпоинт для детального просмотра карточки вакцины, и редактирования по ID."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=[VACCINE_TAG],
        summary='Получить детальную информацию о карточки вакцины.',
        description=(
            'Возвращает полную информацию о карточке вакцины по ID.\n\n'
            'Включает текущую версию со всеми данными: название, производитель, '
            'возрастные ограничения, условия хранения, а также связанные сущности: '
            'инфекции, ингредиенты, противопоказания, методы введения.'
        ),
        responses={
            status.HTTP_200_OK: AdminVaccinesDetailSerializers,
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value={
                    'id': 1,
                    'current_version': 1,
                    'published_version': None,
                    'status': 'draft',
                    'is_visible': False,
                    'version': {
                        'id': 1,
                        'version_number': 1,
                        'version_status': 'draft',
                        'name': 'Инфанрикс Гекса',
                        'official_name': 'Инфанрикс Гекса, суспензия',
                    },
                },
                response_only=True,
                status_codes=[status.HTTP_200_OK],
            ),
        ],
    )
    def get(self, request, id):
        vaccine_card = get_object_or_404(VaccineCard.objects.select_related('current_version'), id=id)
        serializer = AdminVaccinesDetailSerializers(vaccine_card)
        return Response(data=serializer.data)

    @extend_schema(
        tags=[VACCINE_TAG],
        summary='Обновить карточку вакцины',
        description=(
            'Обновляет карточку вакцины по ID.\n\n'
            'Создает новую версию карточки со статусом DRAFT.\n\n'
            'Доступ: только для администраторов.'
        ),
        request=AdminVaccinesCreatedSerializers,
        responses={
            status.HTTP_200_OK: AdminVaccineCreateResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value={'id': 1, 'current_version_id': 2, 'status': 'draft'},
                response_only=True,
                status_codes=[status.HTTP_200_OK],
            ),
        ],
    )
    def put(self, request, id):
        vaccine_card = get_object_or_404(VaccineCard, id=id)
        serializer = AdminVaccinesCreatedSerializers(
            instance=vaccine_card, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        new_version = serializer.save()
        response_serializer = AdminVaccineCreateResponseSerializer(new_version.vaccine_card)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
