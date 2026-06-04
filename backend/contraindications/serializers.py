from rest_framework import serializers

from contraindications.models import Contraindication, ContraindicationCategory
from contraindications.services import get_vaccines_by_contraindication


class ContraindicationCategorySerializer(serializers.ModelSerializer):
    """Преобразует категорию противопоказаний для API."""

    class Meta:
        """Описывает поля категории противопоказаний в API."""

        model = ContraindicationCategory
        fields = ('id', 'name')


class ContraindicationListSerializer(serializers.ModelSerializer):
    """Преобразует противопоказание для списка API."""

    categories = ContraindicationCategorySerializer(many=True, read_only=True)
    searchSelectCount = serializers.IntegerField(
        source='search_select_count',
        read_only=True,
    )
    searchWeight = serializers.DecimalField(
        source='search_weight',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        """Описывает поля противопоказания в списке API."""

        model = Contraindication
        fields = (
            'id',
            'name',
            'categories',
            'searchSelectCount',
            'searchWeight',
        )


class ContraindicationDetailSerializer(ContraindicationListSerializer):
    """Преобразует противопоказание для детального ответа API."""

    vaccines = serializers.SerializerMethodField()

    class Meta(ContraindicationListSerializer.Meta):
        """Добавляет связанные вакцины к полям детального ответа."""

        fields = (*ContraindicationListSerializer.Meta.fields, 'vaccines')

    def get_vaccines(self, obj: Contraindication) -> list[dict]:
        """Возвращает вакцины, связанные с противопоказанием."""
        return get_vaccines_by_contraindication(obj.id)


class ContraindicationSearchSerializer(serializers.ModelSerializer):
    """Преобразует поисковую подсказку противопоказания для API."""

    score = serializers.DecimalField(
        source='search_score',
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        """Описывает поля поисковой подсказки противопоказания."""

        model = Contraindication
        fields = ('id', 'name', 'score')
