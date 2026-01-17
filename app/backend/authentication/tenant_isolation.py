# Correct Company Data Isolation Middleware
# Uses athens_tenant_id for company separation, allowing multiple projects per company

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from .usertype_utils import is_master_type
import logging

logger = logging.getLogger(__name__)

class CompanyTenantIsolationMiddleware(MiddlewareMixin):
    """
    CORRECT: Company isolation using athens_tenant_id
    - Each company has unique athens_tenant_id
    - Companies can have multiple projects
    - Complete data separation between companies
    """
    
    EXEMPT_PATHS = [
        '/admin/',
        '/authentication/login/',
        '/authentication/logout/',
        '/static/',
        '/media/',
        '/api/auth/',
        '/system/',
    ]
    
    def process_request(self, request):
        if self._is_exempt_path(request.path):
            return None
            
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        user = request.user
        
        # Get user's tenant ID (company identifier)
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        
        if not user_tenant_id and not is_master_type(user.user_type):
            logger.warning(f"User {user.username} has no tenant assigned - blocking access")
            return JsonResponse({
                'error': 'NO_TENANT_ACCESS',
                'message': 'User must be assigned to a company tenant',
                'code': 403
            }, status=403)
        
        # Set tenant isolation context
        request.athens_tenant_id = user_tenant_id
        request.is_master_user = is_master_type(user.user_type)
        
        # Apply database-level isolation
        if user_tenant_id:
            self._apply_tenant_isolation(user_tenant_id)
        
        return None
    
    def _is_exempt_path(self, path):
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _apply_tenant_isolation(self, tenant_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET @current_athens_tenant_id = %s", [str(tenant_id)])
                logger.debug(f"Applied tenant isolation for tenant_id: {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to apply tenant isolation: {e}")

def get_tenant_isolated_queryset(queryset, user):
    """
    CORRECT: Apply tenant isolation based on athens_tenant_id
    """
    if not user or not user.is_authenticated:
        return queryset.none()
    
    # Master users can see all data
    if is_master_type(user.user_type):
        return queryset
    
    user_tenant_id = getattr(user, 'athens_tenant_id', None)
    if not user_tenant_id:
        return queryset.none()
    
    model = queryset.model
    
    # Apply tenant-based filtering
    if hasattr(model, 'athens_tenant_id'):
        return queryset.filter(athens_tenant_id=user_tenant_id)
    else:
        logger.warning(f"Model {model.__name__} missing athens_tenant_id field")
        return queryset.none()

class TenantIsolationMixin:
    """
    CORRECT: Tenant-based isolation mixin
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return get_tenant_isolated_queryset(queryset, self.request.user)
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Master users can create for any tenant
        if is_master_type(user.user_type):
            serializer.save()
            return
        
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if not user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be assigned to a company tenant")
        
        # Auto-assign tenant ID
        model = serializer.Meta.model
        if hasattr(model, 'athens_tenant_id'):
            serializer.save(athens_tenant_id=user_tenant_id)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        
        # Master users can update any tenant's data
        if is_master_type(user.user_type):
            serializer.save()
            return
        
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if not user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be assigned to a company tenant")
        
        # Check tenant ownership
        if hasattr(instance, 'athens_tenant_id') and instance.athens_tenant_id != user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot modify data from different company")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        # Master users can delete any tenant's data
        if is_master_type(user.user_type):
            instance.delete()
            return
        
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if not user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be assigned to a company tenant")
        
        # Check tenant ownership
        if hasattr(instance, 'athens_tenant_id') and instance.athens_tenant_id != user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot delete data from different company")
        
        instance.delete()
