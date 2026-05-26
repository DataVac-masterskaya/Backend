from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from reference_books.models import Infection
from rest_framework import viewsets
from rest_framework.response import Response

from .filters import InfectionFilter, OrderingFilterSortBy
from .serializers import InfectionCartSerializer, InfectionSerializer


class InfectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Infection.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilterSortBy)
    filterset_class = InfectionFilter
    ordering_fields = ('name', 'category', 'search_weight')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InfectionCartSerializer
        return InfectionSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Infection.objects.filter(id=instance.id).update(search_select_count=F('search_select_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
