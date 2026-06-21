from django.urls import include, path

urlpatterns = [
    path('audit/', include('api.v1.audit.urls')),
]
