# Enterprise Multi-Tenant Company Isolation Middleware
# Enforces absolute data separation between companies using athens_tenant_id

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from .usertype_utils import is_master_type
import logging

logger = logging.getLogger(__name__)

class CompanyTenantIsolationMiddleware(MiddlewareMixin):
    """
    CORRECT: Enterprise-grade company isolation using athens_tenant_id.
    
    Business Rules:
    - Company A data NEVER mixes with Company B data
    - athens_tenant_id represents Company (EPC/Client/Contractor)
    - Project represents business project (can involve multiple companies)
    - Isolation is structural and enforced at database level
    """
    
    EXEMPT_PATHS = [
        '/admin/',
        '/authentication/login/',
        '/authentication/logout/',
        '/api/saas/',  # SaaS control plane is global, not tenant-bound
        '/static/',
        '/media/',
        '/api/auth/',
        '/system/',
        '/authentication/project/list/',
        '/authentication/induction-status/',
        '/authentication/company-data/',
        '/authentication/companydetail/',
        '/authentication/admin/',
        '/authentication/signature/template/data/',
    ]
    
    def process_request(self, request):
        """Apply tenant-based company isolation to all database queries"""
        
        if self._is_exempt_path(request.path):
            return None
            
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        user = request.user
        
        # Get user's company tenant ID (NOT project_id)
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        
        # SAP MASTER USER: Full access if service is active
        if is_master_type(user.user_type):
            if user_tenant_id:
                # Validate Athens service is still active
                try:
                    from .tenant_models import AthensTenant
                    tenant = AthensTenant.objects.get(id=user_tenant_id)
                    if not tenant.is_active:
                        logger.warning(f"Athens service disabled for tenant {user_tenant_id}")
                        return JsonResponse({
                            'error': 'SERVICE_DISABLED',
                            'message': 'Athens service has been disabled for your company',
                            'code': 403
                        }, status=403)
                except AthensTenant.DoesNotExist:
                    logger.warning(f"Tenant {user_tenant_id} not found")
                    return JsonResponse({
                        'error': 'TENANT_NOT_FOUND',
                        'message': 'Company tenant not found',
                        'code': 403
                    }, status=403)
                except Exception as e:
                    logger.error(f"Database error checking tenant {user_tenant_id}: {e}")
                    return JsonResponse({
                        'error': 'DATABASE_ERROR',
                        'message': 'Database temporarily unavailable',
                        'code': 500
                    }, status=500)
            
            request.athens_tenant_id = user_tenant_id  # Can be None for cross-tenant access
            request.is_master_user = True
            if user_tenant_id:
                self._apply_tenant_isolation(user_tenant_id)
            return None
        
        # ATHENS INTERNAL USERS: Tenant restrictions
        if not user_tenant_id:
            logger.warning(f"User {user.username} has no athens_tenant_id - blocking access")
            return JsonResponse({
                'error': 'NO_TENANT_ACCESS',
                'message': 'User must be assigned to a company tenant',
                'code': 403
            }, status=403)
        
        # Set tenant isolation context
        request.athens_tenant_id = user_tenant_id
        request.is_master_user = False
        
        # Apply database-level tenant isolation
        self._apply_tenant_isolation(user_tenant_id)
        
        return None
    
    def _is_exempt_path(self, path):
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _apply_tenant_isolation(self, tenant_id):
        """Apply database-level tenant isolation using athens_tenant_id"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION current_athens_tenant_id = %s", [str(tenant_id)])
                logger.debug(f"Applied tenant isolation for athens_tenant_id: {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to apply tenant isolation: {e}")

def get_tenant_isolated_queryset(queryset, user):
    """
    CORRECT: Apply tenant isolation based on athens_tenant_id (Company isolation)
    """
    if not user or not user.is_authenticated:
        return queryset.none()

    # Master users can see all data across tenants
    if is_master_type(user.user_type):
        return queryset
    
    user_tenant_id = getattr(user, 'athens_tenant_id', None)
    if not user_tenant_id:
        return queryset.none()
    
    model = queryset.model
    
    # Apply tenant-based filtering (Company isolation)
    if hasattr(model, 'athens_tenant_id'):
        return queryset.filter(athens_tenant_id=user_tenant_id)
    else:
        logger.warning(f"Model {model.__name__} missing athens_tenant_id field - blocking access")
        return queryset.none()


def get_company_isolated_queryset(queryset, user):
    """
    Backwards-compatible alias for tenant-based isolation.
    """
    return get_tenant_isolated_queryset(queryset, user)

class TenantIsolationMixin:
    """
    CORRECT: Enterprise tenant isolation mixin using athens_tenant_id
    
    Enforces absolute company data separation while allowing:
    - Companies to have multiple business projects
    - Projects to involve multiple companies (via explicit role mapping)
    - Master users to access all tenants
    """
    
    def get_queryset(self):
        """Apply tenant-based company isolation"""
        queryset = super().get_queryset()
        return get_tenant_isolated_queryset(queryset, self.request.user)
    
    def perform_create(self, serializer):
        """Ensure created objects belong to user's company tenant"""
        user = self.request.user
        
        # Master users can create for any tenant
        if is_master_type(user.user_type):
            serializer.save()
            return
        
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if not user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be assigned to a company tenant")
        
        # Auto-assign tenant ID to ensure company isolation
        model = serializer.Meta.model
        if hasattr(model, 'athens_tenant_id'):
            serializer.save(athens_tenant_id=user_tenant_id)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ensure updated objects belong to user's company tenant"""
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
        
        # Enforce tenant ownership
        if hasattr(instance, 'athens_tenant_id') and instance.athens_tenant_id != user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot modify data from different company")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure only company's own data can be deleted"""
        user = self.request.user
        
        # Master users can delete any tenant's data
        if is_master_type(user.user_type):
            instance.delete()
            return
        
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if not user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("User must be assigned to a company tenant")
        
        # Enforce tenant ownership
        if hasattr(instance, 'athens_tenant_id') and instance.athens_tenant_id != user_tenant_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot delete data from different company")
        
        instance.delete()
