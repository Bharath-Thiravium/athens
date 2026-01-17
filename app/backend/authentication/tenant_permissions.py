"""
Athens Multi-Tenant Permission Classes

This module provides permission classes for tenant-aware access control.
These permissions ensure that users can only access data within their tenant
and that modules/menus are properly controlled.
"""

from rest_framework import permissions
from .usertype_utils import is_master_user, is_master_type
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .tenant_models import AthensTenant
import jwt
import logging

logger = logging.getLogger(__name__)


class IsTenantMember(permissions.BasePermission):
    """
    Permission class to ensure user belongs to the tenant.
    
    This permission checks that:
    1. Request has athens_tenant_id
    2. User belongs to the same tenant
    3. Tenant is active
    """
    
    message = "You do not have permission to access this tenant's data."
    
    def has_permission(self, request, view):
        """Check if user has permission to access tenant data"""
        # Check if request has tenant context
        if not hasattr(request, 'athens_tenant_id') or not request.athens_tenant_id:
            logger.warning("Request missing athens_tenant_id")
            return False
        
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Master admins can access any tenant (for management purposes)
        if hasattr(request.user, 'admin_type') and request.user.admin_type in ['master', 'masteradmin']:
            return True
        
        # Check if user belongs to the tenant
        if hasattr(request.user, 'athens_tenant_id'):
            if request.user.athens_tenant_id != request.athens_tenant_id:
                logger.warning(
                    f"User {request.user.id} attempted to access tenant {request.athens_tenant_id} "
                    f"but belongs to tenant {request.user.athens_tenant_id}"
                )
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific object"""
        # Check if object is tenant-aware
        if not hasattr(obj, 'athens_tenant_id'):
            logger.warning(f"Object {obj} is not tenant-aware")
            return False
        
        # Check if object belongs to the request tenant
        if obj.athens_tenant_id != request.athens_tenant_id:
            logger.warning(
                f"Object {obj} belongs to tenant {obj.athens_tenant_id} "
                f"but request is for tenant {request.athens_tenant_id}"
            )
            return False
        
        return True


class HasModulePermission(permissions.BasePermission):
    """
    Permission class to check if module is enabled for tenant.
    
    This permission checks that the requested module is enabled
    in the tenant's configuration.
    """
    
    message = "This module is not enabled for your organization."
    
    # Module mapping for different views/endpoints
    MODULE_MAPPING = {
        # Worker management
        'worker': ['worker', 'workers'],
        
        # Training modules
        'inductiontraining': ['induction', 'induction-training'],
        'jobtraining': ['job-training', 'jobtraining'],
        'tbt': ['tbt', 'toolbox-talks'],
        
        # Safety modules
        'safetyobservation': ['safety-observations', 'safety'],
        'incidentmanagement': ['incidentmanagement', 'incidents', 'incident'],
        'inspection': ['inspections', 'inspection'],
        
        # Work management
        'ptw': ['ptw', 'permits'],
        'mom': ['mom', 'minutes'],
        
        # Operations
        'manpower': ['manpower', 'attendance'],
        
        # ESG and Quality
        'environment': ['environment', 'esg'],
        'quality': ['quality', 'qms'],
        
        # Utilities
        'voice_translator': ['translate', 'voice'],
    }
    
    def has_permission(self, request, view):
        """Check if user has permission to access module"""
        # Skip check if no tenant context (handled by other permissions)
        if not hasattr(request, 'athens_tenant') or not request.athens_tenant:
            return True
        
        # Determine required module
        required_module = self._get_required_module(request, view)
        
        if required_module:
            # Check if module is enabled for tenant
            if not request.athens_tenant.is_module_enabled(required_module):
                logger.warning(
                    f"Module {required_module} not enabled for tenant {request.athens_tenant_id}"
                )
                return False
        
        return True
    
    def _get_required_module(self, request, view):
        """Determine which module is required for the request"""
        # Try to get module from view
        if hasattr(view, 'required_module'):
            return view.required_module
        
        # Try to determine from URL path
        path = request.path.lower()
        
        for module, patterns in self.MODULE_MAPPING.items():
            for pattern in patterns:
                if f'/{pattern}/' in path or path.endswith(f'/{pattern}'):
                    return module
        
        # Try to get from view name or class name
        if hasattr(view, '__class__'):
            class_name = view.__class__.__name__.lower()
            for module, patterns in self.MODULE_MAPPING.items():
                if module in class_name:
                    return module
        
        return None


class HasMenuPermission(permissions.BasePermission):
    """
    Permission class to check if menu is enabled for tenant.
    
    This permission is typically used for frontend menu rendering
    but can also be used for API endpoints that correspond to menus.
    """
    
    message = "This menu is not enabled for your organization."
    
    # Menu mapping for different views/endpoints
    MENU_MAPPING = {
        'dashboard': ['dashboard', 'home'],
        'workers': ['worker', 'workers', 'personnel'],
        'training': ['training', 'induction', 'tbt', 'job-training'],
        'safety': ['safety', 'incidents', 'observations', 'inspections'],
        'permits': ['ptw', 'permits', 'work-permits'],
        'reports': ['reports', 'analytics', 'dashboard'],
        'settings': ['settings', 'configuration', 'admin'],
    }
    
    def has_permission(self, request, view):
        """Check if user has permission to access menu"""
        # Skip check if no tenant context
        if not hasattr(request, 'athens_tenant') or not request.athens_tenant:
            return True
        
        # Determine required menu
        required_menu = self._get_required_menu(request, view)
        
        if required_menu:
            # Check if menu is enabled for tenant
            if not request.athens_tenant.is_menu_enabled(required_menu):
                logger.warning(
                    f"Menu {required_menu} not enabled for tenant {request.athens_tenant_id}"
                )
                return False
        
        return True
    
    def _get_required_menu(self, request, view):
        """Determine which menu is required for the request"""
        # Try to get menu from view
        if hasattr(view, 'required_menu'):
            return view.required_menu
        
        # Try to determine from URL path
        path = request.path.lower()
        
        for menu, patterns in self.MENU_MAPPING.items():
            for pattern in patterns:
                if f'/{pattern}/' in path or path.endswith(f'/{pattern}'):
                    return menu
        
        return None


class IsSAPInternal(permissions.BasePermission):
    """
    Permission class for SAP-internal operations only.
    
    This permission ensures that only SAP can perform tenant lifecycle
    operations. Athens is a governed service and should never
    autonomously create or delete tenants.
    """
    
    message = "Only SAP internal systems can perform this operation."
    
    def has_permission(self, request, view):
        """Check if request is from SAP internal system"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check JWT token for SAP internal marker
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # SAP internal operations must have specific markers
            return (
                payload.get('service') == 'athens' and
                payload.get('service_role') == 'SAP_INTERNAL' and
                payload.get('internal_operation') is True
            )
        except Exception:
            return False


class IsMasterAdmin(permissions.BasePermission):
    """
    Permission class for master admin only operations.
    
    This permission is used for tenant management operations
    that should only be accessible to master admins.
    """
    
    message = "Only master administrators can perform this action."
    
    def has_permission(self, request, view):
        """Check if user is a master admin"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'admin_type') and 
            is_master_user(request.user)
        )


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission class for tenant admin operations.
    
    This permission allows tenant admins to manage their tenant's
    configuration and users.
    """
    
    message = "Only tenant administrators can perform this action."
    
    def has_permission(self, request, view):
        """Check if user is a tenant admin"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Master admins have all permissions
        if is_master_user(request.user):
            return True
        
        # Check if user is an admin type for their tenant
        return (
            hasattr(request.user, 'admin_type') and 
            request.user.admin_type in ['client', 'epc', 'contractor']
        )


class CanModifyTenantData(permissions.BasePermission):
    """
    Permission class for modifying tenant data.
    
    This permission ensures users can only modify data within their tenant
    and have the appropriate role permissions.
    """
    
    message = "You do not have permission to modify this data."
    
    def has_permission(self, request, view):
        """Check if user can modify tenant data"""
        # Read operations are generally allowed (handled by other permissions)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check basic tenant membership
        if not hasattr(request, 'athens_tenant_id') or not request.athens_tenant_id:
            return False
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Master admins can modify any tenant's data
        if hasattr(request.user, 'admin_type') and request.user.admin_type in ['master', 'masteradmin']:
            return True
        
        # Check if user belongs to the tenant
        if hasattr(request.user, 'athens_tenant_id'):
            if request.user.athens_tenant_id != request.athens_tenant_id:
                return False
        
        # Check if user has admin privileges
        return (
            hasattr(request.user, 'admin_type') and 
            request.user.admin_type in ['client', 'epc', 'contractor']
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific object"""
        # Read operations are generally allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if object belongs to the request tenant
        if hasattr(obj, 'athens_tenant_id'):
            if obj.athens_tenant_id != request.athens_tenant_id:
                return False
        
        return True


# Composite permission classes for common use cases

class TenantDataAccess(permissions.BasePermission):
    """
    Composite permission for basic tenant data access.
    
    Combines tenant membership and module permission checks.
    """
    
    def has_permission(self, request, view):
        """Check all required permissions"""
        tenant_member = IsTenantMember()
        module_permission = HasModulePermission()
        
        return (
            tenant_member.has_permission(request, view) and
            module_permission.has_permission(request, view)
        )
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        tenant_member = IsTenantMember()
        return tenant_member.has_object_permission(request, view, obj)


class TenantDataModification(permissions.BasePermission):
    """
    Composite permission for tenant data modification.
    
    Combines all necessary checks for modifying tenant data.
    """
    
    def has_permission(self, request, view):
        """Check all required permissions"""
        tenant_member = IsTenantMember()
        module_permission = HasModulePermission()
        can_modify = CanModifyTenantData()
        
        return (
            tenant_member.has_permission(request, view) and
            module_permission.has_permission(request, view) and
            can_modify.has_permission(request, view)
        )
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        tenant_member = IsTenantMember()
        can_modify = CanModifyTenantData()
        
        return (
            tenant_member.has_object_permission(request, view, obj) and
            can_modify.has_object_permission(request, view, obj)
        )
