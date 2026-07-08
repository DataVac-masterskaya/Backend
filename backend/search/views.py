from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from search.serializers import (
    SearchSelectResponseSerializer,
    SearchSelectSerializer,
    SearchSuggestionSerializer,
    SearchSuggestionsResponseSerializer,
)
from search.services import get_search_suggestions, select_search_suggestion


class SearchSuggestionsView(APIView):
    """Отдает глобальные поисковые подсказки, сгруппированные по типам сущностей."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Поисковая строка.',
                required=False,
                type=str,
            ),
        ],
        responses=SearchSuggestionsResponseSerializer,
    )
    def get(self, request):
        """Возвращает подсказки для переданной поисковой строки."""
        query = request.query_params.get('q', '')
        suggestions = get_search_suggestions(query)
        return Response(
            {group: SearchSuggestionSerializer(items, many=True).data for group, items in suggestions.items()},
        )


class SearchSelectView(APIView):
    """Фиксирует выбор пользователем поисковой подсказки."""

    @extend_schema(
        request=SearchSelectSerializer,
        responses=SearchSelectResponseSerializer,
    )
    def post(self, request):
        """Увеличивает счетчик популярности выбранной сущности."""
        serializer = SearchSelectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = select_search_suggestion(
            serializer.validated_data['entityType'],
            serializer.validated_data['entityId'],
        )
        return Response(
            {
                'entityType': serializer.validated_data['entityType'],
                'entityId': entity.id,
                'searchSelectCount': entity.search_select_count,
            },
            status=status.HTTP_200_OK,
        )
