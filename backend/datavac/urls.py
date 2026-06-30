from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/search/', include('search.urls')),
    path('api/v1/', include('api.v1.urls')),
    path('api/v1/', include('vaccines.urls')),
]
