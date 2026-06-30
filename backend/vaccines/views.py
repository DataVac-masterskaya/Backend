from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from vaccines.serializers import AdminVaccinesCreatedSerializers


class AdminVaccineCreateAPIView(APIView):
    """Эндпоинт для создания карточки вакцины."""

    def post(self, request):
        serializer = AdminVaccinesCreatedSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response(
            {'id': version.vaccine_card.id, 'current_version_id': version.id, 'status': version.vaccine_card.status},
            status=status.HTTP_201_CREATED,
        )
