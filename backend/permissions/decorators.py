from functools import wraps
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import PermissionGrant
import logging

logger = logging.getLogger(__name__)

def require_permission(permission_type):
    """Decorator to check if adminuser has permission for edit/delete operations"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            logger.info(f"Permission check: user_type={request.user.user_type}, method={request.method}, permission_type={permission_type}")
            
            if request.user.user_type != 'adminuser':
                logger.info("User is not adminuser, allowing access")
                return view_func(self, request, *args, **kwargs)  # Allow other user types
            
            # Check if adminuser is epcuser - they have full permissions
            if getattr(request.user, 'admin_type', None) == 'epcuser':
                logger.info("User is epcuser adminuser, allowing access")
                return view_func(self, request, *args, **kwargs)
            
            # Extract object info from request
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                lookup_value = kwargs.get('pk') or kwargs.get('id') or kwargs.get('observationID')
                if not lookup_value:
                    logger.error(f"No lookup value found in request kwargs: {kwargs}")
                    return JsonResponse({'error': 'Object ID required'}, status=400)
                
                # Get content type from ViewSet model
                model_class = getattr(self, 'model', None)
                if not model_class:
                    logger.error("No model class found on ViewSet")
                    return JsonResponse({'error': 'Model not specified'}, status=400)
                
                # Get the actual object to find its primary key
                try:
                    lookup_field = getattr(self, 'lookup_field', 'pk')
                    if lookup_field == 'pk':
                        object_id = lookup_value
                    else:
                        # Get the object using the lookup field and extract its primary key
                        obj = model_class.objects.get(**{lookup_field: lookup_value})
                        object_id = obj.pk
                except model_class.DoesNotExist:
                    logger.error(f"Object not found with {lookup_field}={lookup_value}")
                    return JsonResponse({'error': 'Object not found'}, status=404)
                
                content_type = ContentType.objects.get_for_model(model_class)
                logger.info(f"Checking permission for: user={request.user.id}, object_id={object_id}, content_type={content_type}, permission_type={permission_type}")
                
                # Check for valid permission grant
                try:
                    grant = PermissionGrant.objects.select_related('permission_request').get(
                        permission_request__requester=request.user,
                        permission_request__content_type=content_type,
                        permission_request__object_id=object_id,
                        permission_request__permission_type=permission_type,
                        permission_request__status='approved',
                        used=False,
                        expires_at__gt=timezone.now()
                    )
                    
                    logger.info(f"Valid permission grant found: {grant.id}")
                    
                    # Mark as used
                    grant.used = True
                    grant.used_at = timezone.now()
                    grant.save()
                    
                    return view_func(self, request, *args, **kwargs)
                    
                except PermissionGrant.DoesNotExist:
                    logger.warning(f"No valid permission grant found for user {request.user.id}")
                    return JsonResponse({
                        'error': f'Permission required for {permission_type} operation',
                        'action': 'request_permission',
                        'permission_type': permission_type,
                        'object_id': object_id,
                        'content_type': f"{content_type.app_label}.{content_type.model}"
                    }, status=403)
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator