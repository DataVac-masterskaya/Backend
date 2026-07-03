from http import HTTPStatus
import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

# pyrefly: ignore [missing-import]
from audit.models import AuditLog

from typing import cast
from django.contrib.auth.models import AbstractUser

User = cast(type[AbstractUser], get_user_model())
AUDIT_LOGS_URL = '/api/v1/audit/audit-logs/'

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
        AuditLog.objects.create(action_type='test_action', entity_type='test', entity_id=1, user=None)
        response = admin_client.get(AUDIT_LOGS_URL)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        first_record = data[0]
        assert 'id' in first_record
        assert 'user' in first_record
        assert 'entity_type' in first_record
        assert 'entity_id' in first_record
        assert 'action_type' in first_record
        assert 'details' in first_record
        assert 'created_at' in first_record
