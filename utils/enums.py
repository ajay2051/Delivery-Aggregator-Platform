from enum import Enum


class UserRole(Enum):
    partner = "partner"
    super_admin = "super_admin"
    admin = "admin"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]