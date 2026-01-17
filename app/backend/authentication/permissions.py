from rest_framework import permissions
from .usertype_utils import is_master_user

class IsMasterAdmin(permissions.BasePermission):
    """
    Allows access only to master admin users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            is_master_user(request.user)
        )

def require_master_admin(view_func):
    """
    Decorator for function-based views that require master admin.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not (
            request.user and
            request.user.is_authenticated and
            is_master_user(request.user)
        ):
            return permissions.PermissionDenied("You do not have master admin privileges.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to users with user_type 'adminuser'.
    This is for users created by Project Admins (client, epc, contractor).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'adminuser')

class IsProjectAdmin(permissions.BasePermission):
    """
    Allows access only to users with user_type 'projectadmin'.
    These are the client, epc, or contractor admins for a project.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'projectadmin')


class IsSuperAdmin(permissions.BasePermission):
    """
    Platform-level superadmin for SaaS control plane.
    Explicitly checks user_type to avoid relying only on is_staff/is_superuser.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'superadmin')
