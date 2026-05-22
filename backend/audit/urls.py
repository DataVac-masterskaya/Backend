from rest_framework.routers import SimpleRouter

from .views import AuditLogViewSet

app_name = 'audit'

router = SimpleRouter()

router.register(r'audit', AuditLogViewSet, basename='audit-log')

urlpatterns = router.urls
