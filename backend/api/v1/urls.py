from django.urls import include, path
from rest_framework import routers

from .views import InfectionViewSet, IngredientsViewSet, SearchSelectView

router = routers.DefaultRouter()
router.register('infections', InfectionViewSet, basename='infections')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('contraindications.urls')),
    path('', include('instructions.urls')),
    path('search/select', SearchSelectView.as_view(), name='search-select'),
]
