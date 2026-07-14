from django.urls import include, path

from vaccines.views.admin_views import AdminVaccineCreateAPIView, AdminVaccineDetailAPIView
from vaccines.views.publish_views import PublicVaccineDetailView, PublishVaccinesViews

admin_urls = [
    path('cards/', AdminVaccineCreateAPIView.as_view(), name='admin-vaccine-cards'),
    path('cards/<int:id>/', AdminVaccineDetailAPIView.as_view(), name='admin-vaccine-detail'),
]


publish_urls = [
    path('vaccines/', PublishVaccinesViews.as_view(), name='publish-vaccine'),
    path('vaccines/<int:pk>/', PublicVaccineDetailView.as_view(), name='publish-vaccine-detail'),
]

urlpatterns = [
    path('admin/', include(admin_urls)),
    path('', include(publish_urls)),
]
