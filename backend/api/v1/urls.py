from django.urls import include, path
from rest_framework import routers

from .views import InfectionViewSet, IngredientsViewSet

router = routers.DefaultRouter()
router.register('infections', InfectionViewSet, basename='infections')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('contraindications.urls')),
    path('', include('instructions.urls')),
]
