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
    """Преобразует противопоказание для старого списка API."""

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


class ContraindicationFrontendListSerializer(serializers.ModelSerializer):
    """Преобразует противопоказание по контракту фронтенда."""

    category = serializers.SerializerMethodField()
    popularity = serializers.IntegerField(
        source='search_select_count',
        read_only=True,
    )

    class Meta:
        """Описывает поля противопоказания для нового списка API."""

        model = Contraindication
        fields = (
            'id',
            'name',
            'category',
            'subcategory',
            'popularity',
        )

    def get_category(self, obj: Contraindication) -> dict | None:
        """Возвращает первую категорию в алфавитном порядке."""
        categories = list(obj.categories.all())
        if not categories:
            return None
        return ContraindicationCategorySerializer(categories[0]).data


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


class ContraindicationSearchQuerySerializer(serializers.Serializer):
    """Проверяет параметры запроса поисковых подсказок."""

    q = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class VaccineContraindicationSerializer(serializers.Serializer):
    """Описывает противопоказание в краткой карточке вакцины."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()


class VaccineAdministrationMethodSerializer(serializers.Serializer):
    """Описывает способ введения в краткой карточке вакцины."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    ageGroup = serializers.CharField(allow_blank=True, allow_null=True)
    note = serializers.CharField(allow_blank=True, allow_null=True)


class ContraindicationVaccineSerializer(serializers.Serializer):
    """Описывает вакцину в ответе списка вакцин по противопоказанию."""

    id = serializers.IntegerField()
    name = serializers.CharField(allow_blank=True, allow_null=True)
    officialName = serializers.CharField(allow_blank=True, allow_null=True)
    minAge = serializers.IntegerField(allow_null=True)
    maxAge = serializers.IntegerField(allow_null=True)
    pregnancyUsageStatus = serializers.CharField(allow_blank=True, allow_null=True)
    contraindications = VaccineContraindicationSerializer(many=True)
    administrationMethods = VaccineAdministrationMethodSerializer(many=True)


class ContraindicationVaccinesResponseSerializer(serializers.Serializer):
    """Описывает ответ списка вакцин по противопоказанию."""

    contraindicationId = serializers.IntegerField()
    vaccines = ContraindicationVaccineSerializer(many=True)


class SelectCounterResponseSerializer(serializers.Serializer):
    """Описывает ответ обновления счетчика выбора."""

    id = serializers.IntegerField()
    searchSelectCount = serializers.IntegerField()

    class Meta:
        ref_name = 'ContraindicationSelectCounterResponse'
