from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint for Docker containers and load balancers
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Check cache (Redis) connection
        try:
            cache.set('health_check', 'ok', 10)
            cache_status = cache.get('health_check') == 'ok'
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")
            cache_status = False
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_status else 'warning',
            'message': 'All systems operational'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)