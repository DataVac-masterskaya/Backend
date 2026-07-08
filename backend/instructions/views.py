from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from instructions.models import OfficialInstruction
from instructions.serializers import (
    OfficialInstructionDetailSerializer,
    OfficialInstructionListSerializer,
    OfficialInstructionSearchSerializer,
    OfficialInstructionVaccinesResponseSerializer,
    SelectCounterResponseSerializer,
)
from instructions.services import (
    get_vaccines_by_official_instruction,
    increment_official_instruction_select_count,
    search_official_instructions,
)


class OfficialInstructionListView(APIView):
    """Отдает список официальных инструкций."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='source',
                description='Фильтр по источнику инструкции.',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='search',
                description='Поиск по названию инструкции.',
                required=False,
                type=str,
            ),
        ],
        responses=OfficialInstructionListSerializer(many=True),
    )
    def get(self, request):
        """Возвращает официальные инструкции с фильтрацией и поиском."""
        instructions = OfficialInstruction.objects.order_by('title')
        source = request.query_params.get('source')
        search = request.query_params.get('search')

        if source:
            instructions = instructions.filter(source__iexact=source.strip())

        if search:
            instructions = instructions.filter(
                title__icontains=search.strip(),
            )

        serializer = OfficialInstructionListSerializer(instructions, many=True)
        return Response(serializer.data)


class OfficialInstructionDetailView(APIView):
    """Отдает детальную информацию об официальной инструкции."""

    @extend_schema(responses=OfficialInstructionDetailSerializer)
    def get(self, request, pk: int):
        """Возвращает официальную инструкцию и связанные вакцины."""
        instruction = get_object_or_404(OfficialInstruction, id=pk)
        serializer = OfficialInstructionDetailSerializer(instruction)
        return Response(serializer.data)


class OfficialInstructionVaccinesView(APIView):
    """Отдает список вакцин по выбранной официальной инструкции."""

    @extend_schema(responses=OfficialInstructionVaccinesResponseSerializer)
    def get(self, request, pk: int):
        """Возвращает вакцины, связанные с официальной инструкцией."""
        instruction = get_object_or_404(OfficialInstruction, id=pk)
        return Response(
            {
                'instructionId': instruction.id,
                'vaccines': get_vaccines_by_official_instruction(
                    instruction.id,
                ),
            },
        )


class OfficialInstructionSearchView(APIView):
    """Отдает поисковые подсказки по официальным инструкциям."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Поисковая строка.',
                required=False,
                type=str,
            ),
        ],
        responses=OfficialInstructionSearchSerializer(many=True),
    )
    def get(self, request):
        """Возвращает до шести подсказок по поисковой строке."""
        query = request.query_params.get('q', '')
        serializer = OfficialInstructionSearchSerializer(
            search_official_instructions(query),
            many=True,
        )
        return Response(serializer.data)


class SelectOfficialInstructionView(APIView):
    """Фиксирует выбор официальной инструкции в поисковой подсказке."""

    @extend_schema(request=None, responses=SelectCounterResponseSerializer)
    def post(self, request, pk: int):
        """Увеличивает счетчик выбора официальной инструкции."""
        instruction = increment_official_instruction_select_count(pk)
        return Response(
            {
                'id': instruction.id,
                'searchSelectCount': instruction.search_select_count,
            },
        )
