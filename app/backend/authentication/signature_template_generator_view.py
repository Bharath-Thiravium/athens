from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetail, AdminDetail
from .signature_template_generator_new import create_user_signature_template, create_admin_signature_template
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_signature_template(request):
    """Generate digital signature template image"""
    try:
        user = request.user
        logger.info(f"Signature generation requested by user {user.id} - {user.username}")
        
        # Check user type and get/create detail record
        if user.user_type == 'adminuser':
            try:
                user_detail = UserDetail.objects.get(user=user)
            except UserDetail.DoesNotExist:
                # Create UserDetail if it doesn't exist
                user_detail = UserDetail.objects.create(user=user)
                logger.info(f"Created UserDetail for user {user.username}")
            
            # Validate required fields
            if not all([user.name, user.designation]):
                logger.warning(f"Missing required fields for user {user.username}")
                return Response({
                    'error': 'Please complete your profile (name and designation required)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate template
            try:
                create_user_signature_template(user_detail)
                template_url = user_detail.signature_template.url if user_detail.signature_template else None
                logger.info(f"User signature template generated successfully: {template_url}")
            except Exception as e:
                logger.error(f"Failed to generate user signature template: {e}", exc_info=True)
                return Response({
                    'error': f'Template generation failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif user.user_type == 'projectadmin':
            try:
                admin_detail = AdminDetail.objects.get(user=user)
            except AdminDetail.DoesNotExist:
                # Create AdminDetail if it doesn't exist
                admin_detail = AdminDetail.objects.create(user=user)
                logger.info(f"Created AdminDetail for user {user.username}")
            
            # Validate required fields
            if not user.name:
                logger.warning(f"Missing name for admin user {user.username}")
                return Response({
                    'error': 'Please complete your profile (name required)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate template
            try:
                create_admin_signature_template(admin_detail)
                template_url = admin_detail.signature_template.url if admin_detail.signature_template else None
                logger.info(f"Admin signature template generated successfully: {template_url}")
            except Exception as e:
                logger.error(f"Failed to generate admin signature template: {e}", exc_info=True)
                return Response({
                    'error': f'Template generation failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            logger.error(f"Invalid user type {user.user_type} for user {user.username}")
            return Response({
                'error': 'Invalid user type for signature template generation'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify template was actually created
        if not template_url:
            logger.error(f"Template generation completed but no URL returned for user {user.username}")
            return Response({
                'error': 'Template generation failed - no image created'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Signature template generation completed successfully for user {user.username}")
        
        return Response({
            'success': True,
            'message': 'Digital signature template generated successfully',
            'template_url': template_url
        })
        
    except Exception as e:
        logger.error(f"Unexpected error generating signature template for {request.user.username}: {e}", exc_info=True)
        return Response({
            'error': 'Failed to generate signature template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)