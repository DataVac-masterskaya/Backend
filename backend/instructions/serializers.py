from rest_framework import serializers

from instructions.models import OfficialInstruction
from instructions.services import get_vaccines_by_official_instruction


class OfficialInstructionListSerializer(serializers.ModelSerializer):
    """Преобразует официальную инструкцию для списка API."""

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
        """Описывает поля официальной инструкции в списке API."""

        model = OfficialInstruction
        fields = (
            'id',
            'title',
            'url',
            'source',
            'description',
            'searchSelectCount',
            'searchWeight',
        )


class OfficialInstructionDetailSerializer(OfficialInstructionListSerializer):
    """Преобразует официальную инструкцию для детального ответа API."""

    vaccines = serializers.SerializerMethodField()

    class Meta(OfficialInstructionListSerializer.Meta):
        """Добавляет связанные вакцины к полям детального ответа."""

        fields = (*OfficialInstructionListSerializer.Meta.fields, 'vaccines')

    def get_vaccines(self, obj: OfficialInstruction) -> list[dict]:
        """Возвращает вакцины, связанные с официальной инструкцией."""
        return get_vaccines_by_official_instruction(obj.id)


class OfficialInstructionSearchSerializer(serializers.ModelSerializer):
    """Преобразует поисковую подсказку официальной инструкции."""

    score = serializers.DecimalField(
        source='search_score',
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        """Описывает поля поисковой подсказки официальной инструкции."""

        model = OfficialInstruction
        fields = ('id', 'title', 'url', 'source', 'score')
