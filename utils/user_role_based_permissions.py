from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class SuperAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("User not authenticated")

        allowed_roles = ['super_admin']
        if request.user.role in allowed_roles:
            return True

        raise PermissionDenied("You do not have permission to access this resource")


class AdminUserPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("User not authenticated")

        if request.user.role == 'admin':
            return True

        raise PermissionDenied("You do not have permission to access this resource")


class PartnerUserPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("User not authenticated")

        if request.user.role == 'partner':
            return True

        raise PermissionDenied("You do not have permission to access this resource")
