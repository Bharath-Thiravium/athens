from rest_framework import permissions

class CanManageManpower(permissions.BasePermission):
    """
    Custom permission to allow:
    1. Only adminuser (clientuser, epcuser, contractoruser) can create/edit manpower entries
    2. projectadmin can only view manpower entries (read-only access)
    3. Users can only manage manpower entries they created
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Debug information
        
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only adminuser can create/edit manpower entries (not projectadmin)
        if hasattr(request.user, 'user_type') and request.user.user_type == 'adminuser':
            # Allow adminuser with specific admin_type to create/edit manpower entries
            if hasattr(request.user, 'admin_type') and request.user.admin_type in [
                'clientuser', 'epcuser', 'contractoruser'
            ]:
                return True
        
        # Also allow users with the manage_manpower permission (for superusers)
        return request.user.has_perm('manpower.manage_manpower')
    
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Debug information
        
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only adminuser can edit manpower entries (not projectadmin)
        if hasattr(request.user, 'user_type') and request.user.user_type == 'adminuser':
            # Allow adminuser with specific admin_type to edit manpower entries they created
            if hasattr(request.user, 'admin_type') and request.user.admin_type in [
                'clientuser', 'epcuser', 'contractoruser'
            ]:
                # Users can only edit manpower entries they created
                return obj.created_by == request.user
        
        # Also allow users with the manage_manpower permission (for superusers)
        return request.user.has_perm('manpower.manage_manpower')
