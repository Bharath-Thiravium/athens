from rest_framework import permissions

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if user has admin permissions
        if request.user.has_perm('tbt.change_toolboxtalk'):
            return True
            
        # Check if user is a client, epc, or contractor user
        if hasattr(request.user, 'admin_type') and request.user.admin_type in [
            'clientuser', 'epcuser', 'contractoruser'
        ]:
            return True
            
        # Write permissions are only allowed to the creator
        return obj.created_by == request.user