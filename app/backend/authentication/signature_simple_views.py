from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, UserDetail, AdminDetail
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_signature_template_simple(request):
    """Simple template creation that works"""
    try:
        user = request.user
        
        # For adminuser type, create UserDetail template
        if user.user_type == 'adminuser':
            user_detail, created = UserDetail.objects.get_or_create(user=user)
            
            # Check if template already exists
            if user_detail.signature_template:
                return Response({
                    'success': True,
                    'message': 'Template already exists',
                    'template_url': request.build_absolute_uri(user_detail.signature_template.url)
                })
            
            # Create template using the generator
            try:
                from .signature_template_generator_new import SignatureTemplateGenerator
                generator = SignatureTemplateGenerator()
                template_file, template_data = generator.create_signature_template(user_detail)
                
                # Save the template
                user_detail.signature_template.save(template_file.name, template_file, save=False)
                user_detail.signature_template_data = template_data
                user_detail.save()
                
                return Response({
                    'success': True,
                    'message': 'Template created successfully',
                    'template_url': request.build_absolute_uri(user_detail.signature_template.url)
                })
                
            except Exception as e:
                logger.error(f"Template generation error: {str(e)}")
                return Response({
                    'success': False,
                    'error': f'Template generation failed: {str(e)}'
                }, status=500)
        
        # For projectadmin type, create AdminDetail template
        elif user.user_type == 'projectadmin':
            admin_detail, created = AdminDetail.objects.get_or_create(user=user)
            
            if admin_detail.signature_template:
                return Response({
                    'success': True,
                    'message': 'Template already exists',
                    'template_url': request.build_absolute_uri(admin_detail.signature_template.url)
                })
            
            try:
                from .signature_template_generator_new import SignatureTemplateGenerator
                generator = SignatureTemplateGenerator()
                template_file, template_data = generator.create_admin_signature_template(admin_detail)
                
                admin_detail.signature_template.save(template_file.name, template_file, save=False)
                admin_detail.signature_template_data = template_data
                admin_detail.save()
                
                return Response({
                    'success': True,
                    'message': 'Template created successfully',
                    'template_url': request.build_absolute_uri(admin_detail.signature_template.url)
                })
                
            except Exception as e:
                logger.error(f"Admin template generation error: {str(e)}")
                return Response({
                    'success': False,
                    'error': f'Admin template generation failed: {str(e)}'
                }, status=500)
        
        else:
            return Response({
                'success': False,
                'error': f'Unsupported user type: {user.user_type}'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Template creation error: {str(e)}")
        return Response({
            'success': False,
            'error': f'Template creation failed: {str(e)}'
        }, status=500)