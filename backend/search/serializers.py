from rest_framework import serializers


class SearchSuggestionSerializer(serializers.Serializer):
    """Преобразует универсальную поисковую подсказку для API."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    score = serializers.DecimalField(max_digits=20, decimal_places=2)


class SearchSelectSerializer(serializers.Serializer):
    """Проверяет данные выбранной пользователем поисковой подсказки."""

    entityType = serializers.ChoiceField(
        choices=(
            ('contraindication', 'contraindication'),
            ('infection', 'infection'),
            ('ingredient', 'ingredient'),
            ('instruction', 'instruction'),
            ('vaccineCard', 'vaccineCard'),
        ),
    )
    entityId = serializers.IntegerField(min_value=1)

    class Meta:
        ref_name = 'GlobalSearchSelect'


class SearchSuggestionsResponseSerializer(serializers.Serializer):
    """Описывает сгруппированный ответ глобального поиска."""

    contraindications = SearchSuggestionSerializer(many=True)
    infections = SearchSuggestionSerializer(many=True)
    ingredients = SearchSuggestionSerializer(many=True)
    instructions = SearchSuggestionSerializer(many=True)
    vaccines = SearchSuggestionSerializer(many=True)


class SearchSelectResponseSerializer(serializers.Serializer):
    """Описывает ответ фиксации выбора поисковой подсказки."""

    entityType = serializers.CharField()
    entityId = serializers.IntegerField()
    searchSelectCount = serializers.IntegerField()

    class Meta:
        ref_name = 'GlobalSearchSelectResponse'
