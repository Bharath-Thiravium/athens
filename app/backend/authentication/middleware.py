import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log all requests to menu endpoints
        if '/menu' in request.path or request.path.startswith('/api/menu'):
            logger.info(f"MENU REQUEST: {request.method} {request.path}")
            if request.method == 'POST':
                logger.info(f"POST DATA: {request.body.decode('utf-8', errors='replace')[:500]}")
        
        response = self.get_response(request)
        return response

class SecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Basic security audit logging
        logger.info(f"SECURITY AUDIT: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
        response = self.get_response(request)
        return response

class ProjectIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Project isolation logic here
        response = self.get_response(request)
        return response