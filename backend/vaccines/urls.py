from django.urls import path

from vaccines.views import AdminVaccineCreateAPIView

urlpatterns = [
    path(
        'admin/vaccine-cards/',
        AdminVaccineCreateAPIView.as_view(),
        name='admin-vaccine-cards',
    ),
]
