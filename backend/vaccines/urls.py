from django.urls import include, path

from vaccines.views.admin_views import AdminVaccineCreateAPIView, AdminVaccineDetailAPIView
from vaccines.views.publish_views import (
    PublicVaccineDetailView,
    PublishVaccinesViews,
    VaccineInstructionPatientView,
    VaccineInstructionSpecialistView,
    VaccineInstructionView,
    VaccinePDFView,
)

admin_urls = [
    path('cards/', AdminVaccineCreateAPIView.as_view(), name='admin-vaccine-cards'),
    path('cards/<int:id>/', AdminVaccineDetailAPIView.as_view(), name='admin-vaccine-detail'),
]


publish_urls = [
    path('vaccines/', PublishVaccinesViews.as_view(), name='publish-vaccine'),
    path('vaccines/<int:pk>/', PublicVaccineDetailView.as_view(), name='publish-vaccine-detail'),
    path('vaccines/<int:id>/pdf/', VaccinePDFView.as_view(), name='vaccine-pdf'),
    path('vaccines/<int:id>/official-link/', VaccineInstructionView.as_view(), name='official-link'),
    path('vaccines/<int:id>/instruction-patient', VaccineInstructionPatientView.as_view(), name='instruction-patient'),
    path(
        'vaccines/<int:id>/instruction-specialist',
        VaccineInstructionSpecialistView.as_view(),
        name='instruction-specialist',
    ),
]

urlpatterns = [
    path('admin/', include(admin_urls)),
    path('', include(publish_urls)),
]
