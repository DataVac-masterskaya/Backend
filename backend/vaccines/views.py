from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from vaccines.models import VaccineCard
from vaccines.serializers import AdminVaccinesCreatedSerializers, AdminVaccinesDetailSerializers


class AdminVaccineCreateAPIView(APIView):
    """Эндпоинт для создания карточки вакцины."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AdminVaccinesCreatedSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response(
            {'id': version.vaccine_card.id, 'current_version_id': version.id, 'status': version.vaccine_card.status},
            status=status.HTTP_201_CREATED,
        )


class AdminVaccineDetailAPIView(APIView):
    def get(self, request, id):
        vaccine_card = get_object_or_404(VaccineCard.objects.select_related('current_version'), id=id)
        serializer = AdminVaccinesDetailSerializers(vaccine_card)
        return Response(data=serializer.data)
