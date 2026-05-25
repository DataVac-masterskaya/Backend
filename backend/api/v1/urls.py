from django.urls import include, path

urlpatterns = [
    path('admin/', include('api.v1.admin.urls')),
]
