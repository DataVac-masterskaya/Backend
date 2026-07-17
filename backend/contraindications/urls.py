from django.urls import path

from contraindications.views import (
    ContraindicationCategoryListView,
    ContraindicationDetailView,
    ContraindicationLegacyListView,
    ContraindicationListView,
    ContraindicationSearchView,
    ContraindicationVaccinesView,
    SelectContraindicationView,
)

# `contraindications` - публичный API-префикс справочника противопоказаний.
urlpatterns = [
    path(
        'contraindications/categories/',
        ContraindicationCategoryListView.as_view(),
        name='contraindication-category-list',
    ),
    path(
        'contraindications/',
        ContraindicationListView.as_view(),
        name='contraindication-list',
    ),
    path(
        'contraindications/legacy/',
        ContraindicationLegacyListView.as_view(),
        name='contraindication-legacy-list',
    ),
    path(
        'contraindications/search/',
        ContraindicationSearchView.as_view(),
        name='contraindication-search',
    ),
    path(
        'contraindications/<int:pk>/',
        ContraindicationDetailView.as_view(),
        name='contraindication-detail',
    ),
    path(
        'contraindications/<int:pk>/vaccines/',
        ContraindicationVaccinesView.as_view(),
        name='contraindication-vaccines',
    ),
    path(
        'contraindications/<int:pk>/select/',
        SelectContraindicationView.as_view(),
        name='contraindication-select',
    ),
]
