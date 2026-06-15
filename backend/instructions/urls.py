from django.urls import path

from instructions.views import (
    OfficialInstructionDetailView,
    OfficialInstructionListView,
    OfficialInstructionSearchView,
    OfficialInstructionVaccinesView,
    select_official_instruction,
)

urlpatterns = [
    path(
        'instructions/official/',
        OfficialInstructionListView.as_view(),
        name='official-instruction-list',
    ),
    path(
        'instructions/official/search/',
        OfficialInstructionSearchView.as_view(),
        name='official-instruction-search',
    ),
    path(
        'instructions/official/<int:pk>/',
        OfficialInstructionDetailView.as_view(),
        name='official-instruction-detail',
    ),
    path(
        'instructions/official/<int:pk>/vaccines/',
        OfficialInstructionVaccinesView.as_view(),
        name='official-instruction-vaccines',
    ),
    path(
        'instructions/official/<int:pk>/select/',
        select_official_instruction,
        name='official-instruction-select',
    ),
]
