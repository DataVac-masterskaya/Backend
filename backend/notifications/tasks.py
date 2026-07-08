# from celery import shared_task

# from .services.notification_service import NotificationService

# @shared_task
# def send_notification_async(recipient_id, entity_id, notification_type, data):
# from django.contrib.auth import get_user_model
# User = get_user_model()
# recipient = User.objects.get(pk=recipient_id)
# NotificationService.send_sync(recipient, entity_id, notification_type, data)
