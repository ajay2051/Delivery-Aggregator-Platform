from enum import Enum


class UserRole(Enum):
    partner = "partner"
    super_admin = "super_admin"
    admin = "admin"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DeliveryStatus(Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


