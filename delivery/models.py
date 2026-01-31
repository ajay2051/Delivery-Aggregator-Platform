from django.db import models
from rest_framework.exceptions import ValidationError

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

    VALID_TRANSITIONS = {
        DeliveryStatus.CREATED.value: [DeliveryStatus.ASSIGNED.value],
        DeliveryStatus.ASSIGNED.value: [DeliveryStatus.IN_TRANSIT.value],
        DeliveryStatus.IN_TRANSIT.value: [DeliveryStatus.COMPLETED.value, DeliveryStatus.FAILED.value],
        DeliveryStatus.COMPLETED.value: [],  # Terminal state
        DeliveryStatus.FAILED.value: [],  # Terminal state
    }

    # Terminal states that cannot be changed
    TERMINAL_STATES = [DeliveryStatus.COMPLETED.value, DeliveryStatus.FAILED.value]

    def can_transition_to(self, new_status):
        """Check if transition from current status to new status is valid."""
        if self.status in self.TERMINAL_STATES:
            return False, f"Cannot update delivery in {self.status} state"
        valid_next_states = self.VALID_TRANSITIONS.get(self.status, [])
        if new_status not in valid_next_states:
            return False, f"Invalid transition from {self.status} to {new_status}. Valid transitions: {', '.join(valid_next_states) if valid_next_states else 'None'}"
        return True, "Valid transition"

    def validate_status_transition(self, new_status):
        """Validate status transition and raise exception if invalid."""
        can_transition, message = self.can_transition_to(new_status)
        if not can_transition:
            raise ValidationError({'status': message})

    def __str__(self):
        return f"Delivery #{self.id} - {self.status}"
