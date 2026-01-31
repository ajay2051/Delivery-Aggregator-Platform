from django.db import models

from delivery_auth.models import BaseModel, AuthUser
from utils.enums import DeliveryStatus


class Delivery(BaseModel):
    status = models.CharField(choices=DeliveryStatus.choices(), default=DeliveryStatus.CREATED.value)
    delivery_date = models.DateField()
    assigned_to = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='assigned_deliveries')
    created_by = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='created_deliveries')

    class Meta:
        db_table = "deliveries"
