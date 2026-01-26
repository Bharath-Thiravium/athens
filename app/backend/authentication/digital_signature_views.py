from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import json
from .models import UserSignature, FormSignature, SignatureAuditLog, UserDetail, AdminDetail

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_signature(request):
    """Save user's digital signature"""
    try:
        signature_data = request.data.get('signature')
        if not signature_data:
            return Response({'error': 'Signature data required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode base64 image
        format, imgstr = signature_data.split(';base64,')
        ext = format.split('/')[-1]
        
        # Create image file
        image_data = base64.b64decode(imgstr)
        image_file = ContentFile(image_data, name=f'{request.user.username}_signature.{ext}')
        
        # Save or update signature
        signature, created = UserSignature.objects.get_or_create(
            user=request.user,
            defaults={'signature_data': signature_data}
        )
        signature.signature_image = image_file
        signature.signature_data = signature_data
        signature.save()
        
        # Log audit
        SignatureAuditLog.objects.create(
            user=request.user,
            action='created',
            details={'created': created},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'success': True,
            'message': 'Signature saved successfully',
            'signature_url': signature.signature_image.url
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signature(request):
    """Get user's signature for preview with normalized fields"""
    try:
        signature = UserSignature.objects.get(user=request.user)
        
        # Get normalized signature data
        user = request.user
        full_name = f"{user.name or ''} {user.surname or ''}".strip() or user.username
        
        # Get employee ID
        employee_id = None
        try:
            if hasattr(user, 'user_detail') and user.user_detail.employee_id:
                employee_id = user.user_detail.employee_id
        except:
            pass
        
        # Get company logo URL
        company_logo_url = None
        logo = _get_company_logo(user)
        if logo:
            company_logo_url = request.build_absolute_uri(logo.url)
        
        return Response({
            'has_signature': True,
            'signature_url': signature.signature_image.url,
            'created_at': signature.created_at,
            # Normalized fields
            'signer_name': full_name,
            'employee_id': employee_id,
            'designation': user.designation,
            'department': user.department,
            'company_logo_url': company_logo_url
        })
    except UserSignature.DoesNotExist:
        return Response({'has_signature': False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_form(request):
    """Sign a specific form"""
    try:
        form_type = request.data.get('form_type')
        form_id = request.data.get('form_id')
        
        if not form_type or not form_id:
            return Response({'error': 'form_type and form_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has signature
        try:
            user_signature = UserSignature.objects.get(user=request.user)
        except UserSignature.DoesNotExist:
            return Response({'error': 'No signature found. Please create signature first.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create form signature record
        form_signature, created = FormSignature.objects.get_or_create(
            user=request.user,
            form_type=form_type,
            form_id=form_id,
            defaults={
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        # Log audit
        SignatureAuditLog.objects.create(
            user=request.user,
            action='used',
            form_signature=form_signature,
            details={
                'form_type': form_type,
                'form_id': form_id,
                'created': created
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'success': True,
            'signature_url': user_signature.signature_image.url,
            'signed_at': form_signature.signed_at,
            'signature_hash': form_signature.signature_hash
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_form_signature(request):
    """Get signature for a specific form (for print view) with normalized fields"""
    try:
        form_type = request.GET.get('form_type')
        form_id = request.GET.get('form_id')
        
        if not form_type or not form_id:
            return Response({'error': 'form_type and form_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get form signature
        form_signature = FormSignature.objects.get(
            form_type=form_type,
            form_id=form_id,
            user=request.user
        )
        
        # Get user signature
        user_signature = UserSignature.objects.get(user=request.user)
        
        # Log print access
        SignatureAuditLog.objects.create(
            user=request.user,
            action='verified',
            form_signature=form_signature,
            details={'access_type': 'print_view'},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Get normalized signature data
        user = request.user
        full_name = f"{user.name or ''} {user.surname or ''}".strip() or user.username
        
        # Get employee ID
        employee_id = None
        try:
            if hasattr(user, 'user_detail') and user.user_detail.employee_id:
                employee_id = user.user_detail.employee_id
        except:
            pass
        
        # Get company logo URL
        company_logo_url = None
        logo = _get_company_logo(user)
        if logo:
            company_logo_url = request.build_absolute_uri(logo.url)
        
        return Response({
            'signature_url': user_signature.signature_image.url,
            'signed_at': form_signature.signed_at.isoformat(),
            'signature_hash': form_signature.signature_hash,
            # Normalized fields
            'signer_name': full_name,
            'employee_id': employee_id,
            'designation': user.designation,
            'department': user.department,
            'company_logo_url': company_logo_url
        })
        
    except FormSignature.DoesNotExist:
        return Response({'error': 'Form not signed'}, status=status.HTTP_404_NOT_FOUND)
    except UserSignature.DoesNotExist:
        return Response({'error': 'Signature not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_print_action(request):
    """Log when a document is printed"""
    try:
        form_type = request.data.get('form_type')
        form_id = request.data.get('form_id')
        
        form_signature = FormSignature.objects.get(
            form_type=form_type,
            form_id=form_id,
            user=request.user
        )
        
        SignatureAuditLog.objects.create(
            user=request.user,
            action='printed',
            form_signature=form_signature,
            details={
                'print_timestamp': request.data.get('timestamp'),
                'browser': request.META.get('HTTP_USER_AGENT', '')
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'success': True})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_company_logo(user):
    """Get company logo based on user type and hierarchy"""
    from .models import CustomUser
    
    # For EPC project admins, inherit from master's CompanyDetail
    if user.user_type == 'projectadmin' and user.admin_type == 'epc':
        try:
            master_admin = CustomUser.objects.filter(admin_type='master').first()
            if master_admin and hasattr(master_admin, 'company_detail'):
                company_detail = master_admin.company_detail
                if company_detail and company_detail.company_logo:
                    return company_detail.company_logo
        except:
            pass
    
    # For other project admins, use their AdminDetail logo
    elif user.user_type == 'projectadmin':
        try:
            admin_detail = user.admin_detail
            if admin_detail and admin_detail.logo:
                return admin_detail.logo
        except:
            pass

    # For EPCuser, inherit directly from master's CompanyDetail
    elif user.user_type == 'adminuser' and user.admin_type == 'epcuser':
        try:
            master_admin = CustomUser.objects.filter(admin_type='master').first()
            if master_admin and hasattr(master_admin, 'company_detail'):
                company_detail = master_admin.company_detail
                if company_detail and company_detail.company_logo:
                    return company_detail.company_logo
        except:
            pass
    
    # For other admin users, get logo from their creator
    elif user.user_type == 'adminuser' and user.created_by:
        return _get_company_logo(user.created_by)

    return None