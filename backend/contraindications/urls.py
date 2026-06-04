from django.urls import path

from contraindications.views import (
    ContraindicationCategoryListView,
    ContraindicationDetailView,
    ContraindicationListView,
    ContraindicationSearchView,
    ContraindicationVaccinesView,
    select_contraindication,
)

# `contra` - короткий публичный API-префикс справочника противопоказаний.
urlpatterns = [
    path(
        'contra/categories/',
        ContraindicationCategoryListView.as_view(),
        name='contra-category-list',
    ),
    path('contra/', ContraindicationListView.as_view(), name='contra-list'),
    path(
        'contra/search/',
        ContraindicationSearchView.as_view(),
        name='contra-search',
    ),
    path(
        'contra/<int:pk>/',
        ContraindicationDetailView.as_view(),
        name='contra-detail',
    ),
    path(
        'contra/<int:pk>/vaccines/',
        ContraindicationVaccinesView.as_view(),
        name='contra-vaccines',
    ),
    path(
        'contra/<int:pk>/select/',
        select_contraindication,
        name='contra-select',
    ),
]
