"""
Centralized Tenant Resolution Utility

This module provides a single point for tenant extraction and validation
across the Athens platform, ensuring consistent tenant isolation.
"""

import logging
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.core.exceptions import ObjectDoesNotExist
from .tenant_models import AthensTenant

logger = logging.getLogger(__name__)


class TenantResolver:
    """
    Centralized tenant resolution and validation.
    
    Handles extraction from authenticated user context only.
    """
    
    @staticmethod
    def extract_tenant_id(request):
        """
        Extract tenant ID from request using multiple sources.
        
        Returns:
            str: Tenant ID in UUID format or None if not found
        """
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            # Fall back to Authorization header for JWT-authenticated requests
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return None

            token = auth_header.split(' ', 1)[1]
            try:
                # Validate the token before decoding
                UntypedToken(token)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except (InvalidToken, TokenError, jwt.PyJWTError) as exc:
                logger.warning(f"Failed to validate JWT for tenant resolution: {exc}")
                return None

            tenant_id = payload.get('tenant_id') or payload.get('athens_tenant_id')
            if tenant_id:
                logger.debug(f"Extracted tenant from JWT payload: {tenant_id}")
                return tenant_id

            project_id = payload.get('project_id')
            if project_id:
                tenant_uuid = TenantResolver._project_id_to_uuid(project_id)
                logger.debug(f"Derived tenant from project_id in JWT: {tenant_uuid}")
                return tenant_uuid

            return None

        tenant_id = getattr(user, 'athens_tenant_id', None)
        if tenant_id:
            logger.debug(f"Extracted tenant from authenticated user: {tenant_id}")
            return tenant_id

        return None
    
    @staticmethod
    def _project_id_to_uuid(project_id):
        """Convert project ID to UUID format for tenant lookup."""
        return f"00000000-0000-0000-0000-{str(project_id).zfill(12)}"
    
    @staticmethod
    def validate_tenant(tenant_id):
        """
        Validate tenant exists and is active.
        
        Args:
            tenant_id (str): Tenant ID to validate
            
        Returns:
            AthensTenant: Tenant instance or None if invalid
        """
        if not tenant_id:
            return None
        
        try:
            tenant = AthensTenant.objects.get(
                id=tenant_id,
                is_active=True
            )
            logger.debug(f"Validated tenant: {tenant_id}")
            return tenant
        except ObjectDoesNotExist:
            logger.warning(f"Tenant not found or inactive: {tenant_id}")
            return None
        except Exception as e:
            logger.error(f"Tenant validation error: {e}")
            return None
    
    @staticmethod
    def resolve_tenant(request):
        """
        Complete tenant resolution: extract and validate.
        
        Args:
            request: Django request object
            
        Returns:
            tuple: (tenant_id, tenant_instance) or (None, None) if not found/invalid
        """
        tenant_id = TenantResolver.extract_tenant_id(request)
        if not tenant_id:
            return None, None
        
        tenant = TenantResolver.validate_tenant(tenant_id)
        return tenant_id, tenant
    
    @staticmethod
    def attach_tenant_context(request, tenant_id, tenant):
        """
        Attach tenant context to request object.
        
        Args:
            request: Django request object
            tenant_id (str): Tenant ID
            tenant (AthensTenant): Tenant instance
        """
        request.athens_tenant_id = tenant_id
        request.athens_tenant = tenant
        user = getattr(request, 'user', None)
        user_state = getattr(user, '_state', None) if user is not None else None
        request.tenant_db = getattr(user_state, 'db', None)
        if hasattr(tenant, 'master_admin_id'):
            request.master_admin_id = tenant.master_admin_id
        
        logger.debug(f"Attached tenant context: {tenant_id}")


class TenantValidationMixin:
    """
    Mixin for views that need tenant validation.
    
    Provides consistent tenant extraction and validation
    across different view types.
    """
    
    def get_tenant_context(self):
        """Get tenant context from request."""
        if not hasattr(self.request, 'athens_tenant'):
            # Attempt to resolve tenant if not already done
            tenant_id, tenant = TenantResolver.resolve_tenant(self.request)
            if tenant:
                TenantResolver.attach_tenant_context(self.request, tenant_id, tenant)
        
        return getattr(self.request, 'athens_tenant', None)
    
    def validate_tenant_access(self, obj=None):
        """
        Validate user has access to tenant and optionally to specific object.
        
        Args:
            obj: Optional object to validate tenant access for
            
        Returns:
            bool: True if access is allowed
        """
        tenant = self.get_tenant_context()
        if not tenant:
            return False
        
        # If object is provided, validate it belongs to the same tenant
        if obj and hasattr(obj, 'project'):
            # Convert project to tenant format for comparison
            obj_tenant_id = TenantResolver._project_id_to_uuid(obj.project.id)
            if obj_tenant_id != str(tenant.id):
                logger.warning(f"Object tenant mismatch: {obj_tenant_id} != {tenant.id}")
                return False
        
        return True
