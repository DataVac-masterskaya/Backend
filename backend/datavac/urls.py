from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('api/', include('api.urls')),
=======
    path('api/v1/', include('api.v1.urls')),
>>>>>>> develop
]
