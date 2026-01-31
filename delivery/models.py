from django.db import models

from delivery_auth.models import BaseModel, AuthUser
from utils.enums import DeliveryStatus


class Delivery(BaseModel):
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(choices=DeliveryStatus.choices(), default=DeliveryStatus.CREATED.value)
    delivery_date = models.DateField()
    delivery_address = models.CharField(max_length=255, null=True, blank=True)
    assigned_to = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='assigned_deliveries', null=True, blank=True)
    created_by = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='created_deliveries', null=True, blank=True)

    class Meta:
        db_table = "deliveries"
        unique_together = [['idempotency_key', 'delivery_date', 'created_by'], ]
