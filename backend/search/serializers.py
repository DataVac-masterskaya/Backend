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
        ),
    )
    entityId = serializers.IntegerField(min_value=1)
