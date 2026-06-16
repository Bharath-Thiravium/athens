from rest_framework import permissions

class SafetyObservationPermission(permissions.BasePermission):
    """
    Allow any authenticated user to access safety observations
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated
