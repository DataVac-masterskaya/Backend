from django.urls import include, path
from rest_framework import routers

from .views import InfectionViewSet

router = routers.DefaultRouter()
router.register('infections', InfectionViewSet, basename='infections')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('instructions.urls')),
]
