import os
import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetail, AdminDetail
from .signature_template_generator_new import SignatureTemplateGenerator, create_signature_template
from .tenant_scoped_utils import enforce_scope_or_403

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_data(request):
    """Get signature template data and status"""
    try:
        # enforce_scope_or_403(request)  # Temporarily disabled for debugging
        user = request.user
        
        # Debug logging
        logger.error(f"template_data DEBUG: user={user.username}, user_type={user.user_type}, admin_type={getattr(user, 'admin_type', None)}")
        
        # Get or create detail record - handle JWT token user_type mapping
        # JWT may have user_type set to admin_type value (clientuser, epcuser, etc.)
        user_type = user.user_type
        admin_type = getattr(user, 'admin_type', None)
        
        # Check if this is a regular user (admin users created by project admins)
        if (user_type in ['adminuser', 'user'] or 
            admin_type in ['clientuser', 'epcuser', 'contractoruser'] or
            user_type in ['clientuser', 'epcuser', 'contractoruser']):
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif (user_type in ['projectadmin', 'master'] or 
              admin_type in ['client', 'epc', 'contractor', 'master']):
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            error_msg = f"Unsupported user type: {user_type}/{admin_type}"
            logger.error(f"template_data ERROR: {error_msg}")
            return Response({
                'success': False,
                'error': error_msg,
                'debug': {
                    'user_type': user_type,
                    'admin_type': admin_type,
                    'username': user.username
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if template can be created
        missing_fields = []
        if not user.name:
            missing_fields.append('Name')
        if user.user_type == 'adminuser' and not user.designation:
            missing_fields.append('Designation')
        
        can_create = len(missing_fields) == 0
        has_template = bool(detail.signature_template)
        
        # Get company logo status
        generator = SignatureTemplateGenerator()
        logo = generator.resolve_company_logo(user)
        has_logo = bool(logo[0] if logo else None)
        
        return Response({
            'success': True,
            'can_create_template': can_create,
            'has_existing_template': has_template,
            'missing_fields': missing_fields,
            'user_data': {
                'full_name': f"{user.name or ''} {user.surname or ''}".strip() or user.username,
                'designation': user.designation or '',
                'company_name': generator._get_company_name(user) or '',
                'has_company_logo': has_logo,
                'employee_id': getattr(detail, 'employee_id', '') or ''
            }
        })
        
    except Exception as e:
        logger.exception(f"Error getting template data for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to load template data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_template(request):
    """Generate new signature template"""
    enforce_scope_or_403(request)
    try:
        user = request.user
        
        # Get or create detail record
        if user.user_type in ['adminuser', 'user'] or user.admin_type in ['clientuser', 'epcuser', 'contractoruser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master'] or user.admin_type in ['client', 'epc', 'contractor', 'master']:
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported user type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate required fields
        if not user.name:
            return Response({
                'success': False,
                'error': 'Name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.user_type == 'adminuser' and not user.designation:
            return Response({
                'success': False,
                'error': 'Designation is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate template
        template_file = create_signature_template(detail)
        template_url = request.build_absolute_uri(detail.signature_template.url)
        
        logger.info(f"Signature template generated for user {user.id}")
        
        return Response({
            'success': True,
            'message': 'Template generated successfully',
            'template_url': template_url
        })
        
    except Exception as e:
        logger.exception(f"Error generating template for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to generate template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_template(request):
    """Preview signature template"""
    try:
        user = request.user
        fresh = request.query_params.get('fresh') == '1'
        
        # Get detail record
        if user.user_type in ['adminuser', 'user'] or user.admin_type in ['clientuser', 'epcuser', 'contractoruser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master'] or user.admin_type in ['client', 'epc', 'contractor', 'master']:
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported user type'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate fresh preview if requested or no template exists
        if fresh or not detail.signature_template or not os.path.exists(detail.signature_template.path):
            generator = SignatureTemplateGenerator()
            template_file, _ = generator.create_signature_template(detail)
            template_file.seek(0)
            
            response = HttpResponse(template_file.read(), content_type='image/png')
            response['Cache-Control'] = 'no-store'
            return response
        
        # Return existing template
        template_url = request.build_absolute_uri(detail.signature_template.url)
        return Response({
            'success': True,
            'template_url': template_url
        })
        
    except Exception as e:
        logger.exception(f"Error previewing template for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to preview template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_template(request):
    """Reset and regenerate signature template"""
    enforce_scope_or_403(request)
    try:
        user = request.user
        
        # Get detail record
        if user.user_type in ['adminuser', 'user'] or user.admin_type in ['clientuser', 'epcuser', 'contractoruser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master'] or user.admin_type in ['client', 'epc', 'contractor', 'master']:
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported user type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old template file
        if detail.signature_template:
            try:
                old_path = detail.signature_template.path
                if os.path.exists(old_path):
                    os.remove(old_path)
                detail.signature_template.delete(save=False)
            except Exception as e:
                logger.warning(f"Error deleting old template for user {user.id}: {e}")
        
        # Clear template fields
        detail.signature_template = None
        if hasattr(detail, 'signature_template_data'):
            detail.signature_template_data = None
        detail.save()
        
        # Regenerate template
        template_file = create_signature_template(detail)
        template_url = request.build_absolute_uri(detail.signature_template.url)
        
        logger.info(f"Template reset and regenerated for user {user.id}")
        
        return Response({
            'success': True,
            'message': 'Template reset and regenerated successfully',
            'template_url': template_url
        })
        
    except Exception as e:
        logger.exception(f"Error resetting template for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to reset template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
