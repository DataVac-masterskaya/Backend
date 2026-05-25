from http import HTTPStatus
import pytest

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

# pyrefly: ignore [missing-import]
from audit.models import AuditLog

User = get_user_model()
AUDIT_LOGS_URL = '/api/v1/admin/audit-logs/'

@pytest.fixture
def normal_user(db) -> User:
    return User.objects.create_user(username='test_user_normal', password='password')

@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_superuser(username='test_admin', password='password')

@pytest.fixture
def anonymous_client() -> APIClient:
    return APIClient()

@pytest.fixture
def normal_client(normal_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=normal_user)
    return client

@pytest.fixture
def admin_client(admin_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.mark.django_db
class TestAuditLog:
    
    def test_audit_log_immutability(self):
        log = AuditLog(action_type='test', entity_type='test', entity_id=1, user=None)
        log.save()
        with pytest.raises(PermissionDenied):
            log.save()

    def test_user_creation_signal(self):
        user = User.objects.create_user(username='testuser', password='password')
        assert AuditLog.objects.filter(action_type='user_create').exists() == True

    def test_anonymous_access_denied(self, anonymous_client):
        response = anonymous_client.get(AUDIT_LOGS_URL)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_normal_user_access_denied(self, normal_client):
        response = normal_client.get(AUDIT_LOGS_URL)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_admin_user_access_allowed(self, admin_client):
        response = admin_client.get(AUDIT_LOGS_URL)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            first_record = data[0]
            assert 'id' in first_record
            assert 'user' in first_record
            assert 'entity_type' in first_record
            assert 'entity_id' in first_record
            assert 'action_type' in first_record
            assert 'details' in first_record
            assert 'created_at' in first_record