from django.urls import include, path
from rest_framework import routers

from .views import InfectionViewSet

router = routers.DefaultRouter()
router.register('infections', InfectionViewSet, basename='infections')

urlpatterns = [
    path('v1/', include(router.urls)),
]
