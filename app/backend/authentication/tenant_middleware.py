"""
Athens Multi-Tenant Middleware

This middleware enforces strict tenant isolation by:
1. Deriving athens_tenant_id from authenticated user context
2. Validating tenant exists and is active
3. Attaching tenant context to requests
4. Blocking access if tenant is invalid
"""

import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .tenant_resolver import TenantResolver

logger = logging.getLogger(__name__)


class AthensTenantMiddleware(MiddlewareMixin):
    """
    Middleware to enforce Athens multi-tenant isolation.
    
    This middleware MUST be placed after authentication middleware
    but before any business logic middleware.
    """
    
    # Paths that don't require tenant validation
    EXEMPT_PATHS = [
        '/admin/',
        '/api/auth/',
        '/api/menu/',  # Menu endpoints
        '/api/saas/',  # SaaS control plane is global, not tenant-scoped
        '/authentication/',  # Exempt ALL authentication endpoints
        '/health/',
        '/static/',
        '/media/',
        '/system/',  # System management endpoints
        '/ws/',  # WebSocket connections handled by WebSocket middleware
        '/favicon.ico',
        '/robots.txt',
    ]
    
    def process_request(self, request):
        """
        Process incoming request to extract and validate tenant context.
        """
        # Skip tenant validation for exempt paths
        if self._is_exempt_path(request.path):
            return None
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None
        
        try:
            # Extract and validate tenant using centralized resolver
            tenant_id, tenant = TenantResolver.resolve_tenant(request)
            
            if not tenant_id:
                logger.warning(f"No athens_tenant_id found in request to {request.path}")
                # Check if user is authenticated first
                if not hasattr(request, 'user') or not request.user.is_authenticated:
                    return JsonResponse({
                        'detail': 'Authentication credentials were not provided.'
                    }, status=401)
                else:
                    return self._tenant_error_response(
                        "Missing athens_tenant_id in request",
                        status=422  # Unprocessable Entity - missing required field
                    )
            
            if not tenant:
                logger.warning(f"Invalid or inactive tenant: {tenant_id}")
                return self._tenant_error_response(
                    "Invalid or inactive tenant",
                    status=403
                )
            
            # Attach tenant context to request
            TenantResolver.attach_tenant_context(request, tenant_id, tenant)
            
            logger.debug(f"Tenant context attached: {tenant_id}")
            
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            return self._tenant_error_response(
                "Tenant validation failed",
                status=500
            )
        
        return None
    
    def _is_exempt_path(self, path):
        """Check if path is exempt from tenant validation"""
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _tenant_error_response(self, message, status=403):
        """Return standardized tenant error response"""
        return JsonResponse({
            'error': 'TENANT_ERROR',
            'message': message,
            'code': status
        }, status=status)


class TenantPermissionMiddleware(MiddlewareMixin):
    """
    Middleware to enforce module and menu permissions based on tenant configuration.
    
    This middleware should be placed after AthensTenantMiddleware.
    """
    
    # Module to URL path mapping
    MODULE_PATHS = {
        'worker': ['/api/workers/', '/api/worker/', '/api/v1/worker/'],
        'tbt': ['/api/tbt/', '/api/toolbox-talks/', '/api/v1/tbt/'],
        'inductiontraining': ['/api/induction/', '/api/induction-training/', '/api/v1/induction/'],
        'jobtraining': ['/api/job-training/', '/api/jobtraining/', '/jobtraining/', '/api/v1/jobtraining/'],
        'mom': ['/api/mom/', '/api/minutes/', '/api/v1/mom/'],
        'safetyobservation': ['/api/safety-observations/', '/api/safety/', '/api/v1/safetyobservation/'],
        'ptw': ['/api/ptw/', '/api/permits/', '/api/v1/ptw/'],
        'manpower': ['/api/manpower/', '/api/attendance/', '/api/v1/manpower/'],
        'incidentmanagement': ['/api/incidents/', '/api/incident/', '/api/v1/incident/', '/api/v1/incidentmanagement/'],
        'inspection': ['/api/inspections/', '/api/inspection/', '/api/v1/inspection/'],
        'environment': ['/api/environment/', '/api/esg/', '/api/v1/environment/'],
        'quality': ['/api/quality/', '/api/qms/', '/api/v1/quality/'],
        'voice_translator': ['/api/translate/', '/api/voice/', '/api/v1/voice/'],
    }
    
    def process_request(self, request):
        """Check if requested module is enabled for tenant"""
        # Skip if no tenant context (handled by AthensTenantMiddleware)
        if not hasattr(request, 'athens_tenant'):
            return None
        
        # Skip for exempt paths
        if self._is_exempt_path(request.path):
            return None
        
        # Check module permissions
        required_module = self._get_required_module(request.path)
        if required_module:
            if not request.athens_tenant.is_module_enabled(required_module):
                logger.warning(
                    f"Module {required_module} not enabled for tenant {request.athens_tenant_id}"
                )
                return JsonResponse({
                    'error': 'MODULE_DISABLED',
                    'message': f'Module {required_module} is not enabled for your organization',
                    'code': 403
                }, status=403)
        
        return None
    
    def _is_exempt_path(self, path):
        """Check if path is exempt from module validation"""
        exempt_paths = [
            '/admin/',
            '/api/auth/',
            '/api/saas/',  # SaaS control plane is global, not tenant-scoped
            '/health/',
            '/api/tenant/',
            '/static/',
            '/media/',
        ]
        return any(path.startswith(exempt) for exempt in exempt_paths)
    
    def _get_required_module(self, path):
        """Determine which module is required for the given path"""
        for module, paths in self.MODULE_PATHS.items():
            if any(path.startswith(module_path) for module_path in paths):
                return module
        return None
