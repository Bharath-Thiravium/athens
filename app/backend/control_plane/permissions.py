from rest_framework import permissions
from authentication.permissions import IsSuperAdmin


class IsPlatformSuperadmin(permissions.BasePermission):
    """
    Platform superadmin for SaaS control plane.
    Uses explicit user_type check to avoid relying on Django superuser flag alone.
    """

    def has_permission(self, request, view):
        return IsSuperAdmin().has_permission(request, view)
