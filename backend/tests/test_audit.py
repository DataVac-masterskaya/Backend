import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

# pyrefly: ignore [missing-import]
from audit.models import AuditLog

User = get_user_model()

@pytest.mark.django_db
class TestAuditLog:
    
    def test_audit_log_immutability(self):
        log = AuditLog(action_type='test', entity_type='test', entity_id=1, user=None, ip_address='127.0.0.1')
        log.save()
        with pytest.raises(PermissionDenied):
            log.save()

    def test_user_creation_signal(self):
        user = User.objects.create_user(username='testuser', password='password')
        assert AuditLog.objects.filter(action_type='user_create').exists() == True

    def test_audit_api_security_and_format(self):
        client = APIClient()
        response = client.get('/audit/')
        assert response.status_code == 403

        normal_user = User.objects.create_user(username='test_user_normal', password='password')
        client.force_authenticate(user=normal_user)
        response = client.get('/audit/')
        assert response.status_code == 403
        
        admin_user = User.objects.create_superuser(username='test_admin', password='password')
        client.force_authenticate(user=admin_user)
        response = client.get('/audit/')
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            first_record = data[0]
            assert 'ip_address' not in first_record
            assert 'user' in first_record
        