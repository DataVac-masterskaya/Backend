from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from vaccines.serializers import AdminVaccineCreateResponseSerializer, AdminVaccinesCreatedSerializers


class AdminVaccineCreateAPIView(APIView):
    """Эндпоинт для создания карточки вакцины."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AdminVaccinesCreatedSerializers,
        responses={status.HTTP_201_CREATED: AdminVaccineCreateResponseSerializer},
    )
    def post(self, request):
        serializer = AdminVaccinesCreatedSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response(
            {'id': version.vaccine_card.id, 'current_version_id': version.id, 'status': version.vaccine_card.status},
            status=status.HTTP_201_CREATED,
        )
