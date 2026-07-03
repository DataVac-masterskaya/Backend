from rest_framework.routers import SimpleRouter

from .views import AuditLogViewSet

app_name = 'audit-api'

router = SimpleRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = router.urls
