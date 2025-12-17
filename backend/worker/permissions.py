from rest_framework import permissions

class CanManageWorkers(permissions.BasePermission):
    """
    Custom permission to allow:
    1. Only adminuser (clientuser, epcuser, contractoruser) can create/edit workers
    2. projectadmin can only view workers (read-only access)
    3. Users can only manage workers they created
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Master admin has full access
        if getattr(request.user, 'admin_type', None) == 'master':
            return True

        # Only admin users can create/edit workers (not project admins)
        user_admin_type = getattr(request.user, 'admin_type', None)
        if user_admin_type in ['clientuser', 'epcuser', 'contractoruser']:
            return True

        # Also allow users with the manage_workers permission (for superusers)
        return request.user.has_perm('worker.manage_workers')

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Master admin has full access
        if getattr(request.user, 'admin_type', None) == 'master':
            return True

        # Only admin users can edit workers (not project admins)
        user_admin_type = getattr(request.user, 'admin_type', None)
        if user_admin_type in ['clientuser', 'epcuser', 'contractoruser']:
            # Users can only edit workers they created
            return obj.created_by == request.user

        # Also allow users with the manage_workers permission (for superusers)
        return request.user.has_perm('worker.manage_workers')
