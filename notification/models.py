from django.db import models
from delivery.models import Delivery
from delivery_auth.models import BaseModel, AuthUser


class Notification(BaseModel):
    NOTIFICATION_TYPES = [
        ('delivery_created', 'Delivery Created'),
        ('delivery_assigned', 'Delivery Assigned'),
        ('status_changed', 'Status Changed'),
        ('delivery_completed', 'Delivery Completed'),
        ('delivery_failed', 'Delivery Failed'),
    ]

    recipient = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='notifications')
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "notifications"

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.email}"