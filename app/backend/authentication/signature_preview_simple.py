from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetail, AdminDetail
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_template_preview_simple(request):
    """Simple template preview that works"""
    try:
        user = request.user
        
        # Check UserDetail for adminuser
        if user.user_type == 'adminuser':
            try:
                user_detail = UserDetail.objects.get(user=user)
                if user_detail.signature_template:
                    template_url = request.build_absolute_uri(user_detail.signature_template.url)
                    return Response({
                        'success': True,
                        'template_url': template_url
                    })
            except UserDetail.DoesNotExist:
                pass
        
        # Check AdminDetail for projectadmin
        elif user.user_type == 'projectadmin':
            try:
                admin_detail = AdminDetail.objects.get(user=user)
                if admin_detail.signature_template:
                    template_url = request.build_absolute_uri(admin_detail.signature_template.url)
                    return Response({
                        'success': True,
                        'template_url': template_url
                    })
            except AdminDetail.DoesNotExist:
                pass
        
        return Response({
            'success': False,
            'error': 'No template found'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)