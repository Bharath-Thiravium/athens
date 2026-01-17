from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import CustomUser, UserDetail, AdminDetail, CompanyDetail
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_template_data(request):
    """Get signature template data for current user"""
    try:
        user = request.user
        
        # Get user data based on user type
        full_name = f"{user.name or ''} {user.surname or ''}".strip() or user.username
        designation = user.designation or ''
        company_name = user.company_name or ''
        has_logo = False
        logo_url = None
        has_template = False
        template_data = None
        
        # Check for existing signature template based on user type
        if user.user_type == 'projectadmin':
            try:
                admin_detail = AdminDetail.objects.get(user=user)
                if admin_detail.signature_template:
                    has_template = True
                    template_data = admin_detail.signature_template_data
                if admin_detail.logo:
                    has_logo = True
                    logo_url = request.build_absolute_uri(admin_detail.logo.url)
            except AdminDetail.DoesNotExist:
                pass
        elif user.user_type == 'adminuser':
            try:
                user_detail = UserDetail.objects.get(user=user)
                if user_detail.signature_template:
                    has_template = True
                    template_data = user_detail.signature_template_data
            except UserDetail.DoesNotExist:
                pass
        
        # Get company logo from hierarchy if not found
        if not has_logo and user.admin_type == 'epc':
            try:
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        has_logo = True
                        logo_url = request.build_absolute_uri(company_detail.company_logo.url)
                        company_name = company_name or company_detail.company_name
            except:
                pass
        
        # Check missing fields
        missing_fields = []
        if not full_name or full_name == user.username:
            missing_fields.append('Full Name')
        if not designation:
            missing_fields.append('Designation')
        if not company_name:
            missing_fields.append('Company Name')
        
        can_create = len(missing_fields) == 0
        
        return Response({
            'can_create_template': can_create,
            'missing_fields': missing_fields,
            'user_data': {
                'full_name': full_name,
                'designation': designation,
                'company_name': company_name,
                'has_company_logo': has_logo,
                'logo_url': logo_url
            },
            'has_existing_template': has_template,
            'template_data': template_data
        })
        
    except Exception as e:
        logger.error(f"Signature template error: {str(e)}")
        return Response({
            'error': 'System error',
            'can_create_template': False,
            'missing_fields': ['System Error'],
            'user_data': {
                'full_name': 'Not set',
                'designation': 'Not set',
                'company_name': 'Not set',
                'has_company_logo': False,
                'logo_url': None
            },
            'has_existing_template': False,
            'template_data': None
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_template_preview(request):
    """Get signature template preview URL"""
    user = request.user
    
    try:
        if hasattr(user, 'user_type') and user.user_type == 'projectadmin':
            admin_detail = AdminDetail.objects.get(user=user)
            if hasattr(admin_detail, 'signature_template') and admin_detail.signature_template:
                return Response({
                    'success': True,
                    'template_url': request.build_absolute_uri(admin_detail.signature_template.url)
                })
        
        return Response({
            'success': False,
            'error': 'No signature template found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except AdminDetail.DoesNotExist:
        return Response({
            'success': False,
            'error': 'No signature template found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in signature_template_preview: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get template preview'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_signature_template(request):
    """Create signature template for user"""
    user = request.user
    
    try:
        # Only project admins can create templates
        if not hasattr(user, 'user_type') or user.user_type != 'projectadmin':
            return Response({
                'success': False,
                'error': 'Only project admins can create signature templates'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create admin detail
        admin_detail, created = AdminDetail.objects.get_or_create(user=user)
        
        # For now, return success without actually generating template
        # Template generation will be handled automatically when user saves profile
        return Response({
            'success': True,
            'message': 'Signature template will be created automatically when you save your profile details'
        })
            
    except Exception as e:
        logger.error(f"Error in create_signature_template: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to create signature template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignatureTemplateDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return signature_template_data(request)

class SignatureTemplatePreviewView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return signature_template_preview(request)

class CreateSignatureTemplateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return create_signature_template(request)