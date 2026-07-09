from django.urls import path

from vaccines.views import AdminVaccineCreateAPIView, AdminVaccineDetailAPIView

urlpatterns = [
    path(
        'admin/vaccine-cards/',
        AdminVaccineCreateAPIView.as_view(),
        name='admin-vaccine-cards',
    ),
    path('admin/vaccine-cards/<int:id>/', AdminVaccineDetailAPIView.as_view(), name='admin-vaccine-detail'),
]
