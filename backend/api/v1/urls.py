from django.urls import include, path
from rest_framework import routers

from .views import InfectionViewSet, IngredientsViewSet, MethodsOfAdministrationViewSet, SearchSelectView

router = routers.DefaultRouter()
router.register('infections', InfectionViewSet, basename='infections')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('admin-methods', MethodsOfAdministrationViewSet, basename='admin-methods')

urlpatterns = [
    path('audit/', include('api.v1.audit.urls')),
    path('', include('contraindications.urls')),
    path('', include('instructions.urls')),
    path('search/select', SearchSelectView.as_view(), name='search-select'),
]
