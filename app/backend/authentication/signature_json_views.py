import os
import logging
import hmac
import hashlib
from datetime import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import UserDetail, AdminDetail
from .signature_template_generator_new import SignatureTemplateGenerator

logger = logging.getLogger(__name__)

def generate_verification_token(user_id, signed_at, context="signature"):
    """Generate HMAC verification token for signature integrity"""
    secret_key = getattr(settings, 'SECRET_KEY', 'fallback-key')
    data = f"{user_id}:{signed_at}:{context}"
    return hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]  # First 16 chars for display

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_json_data(request):
    """Get signature data as JSON (no image generation/storage)"""
    try:
        user = request.user
        
        # Get or create detail record
        if user.user_type in ['adminuser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master']:
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported user type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if signature can be created
        missing_fields = []
        if not user.name:
            missing_fields.append('Name')
        if user.user_type == 'adminuser' and not user.designation:
            missing_fields.append('Designation')
        
        can_create = len(missing_fields) == 0
        
        # Get company logo URL (not generate image)
        generator = SignatureTemplateGenerator()
        logo_file, logo_source, logo_path = generator.resolve_company_logo(user)
        
        # Build company logo URL if available
        company_logo_url = None
        if logo_file and hasattr(logo_file, 'url'):
            try:
                company_logo_url = request.build_absolute_uri(logo_file.url)
            except Exception:
                company_logo_url = logo_file.url  # Fallback to relative URL
        elif logo_path and os.path.exists(logo_path):
            # For fallback logos, we need to serve them via static/media URL
            try:
                relative_path = os.path.relpath(logo_path, settings.MEDIA_ROOT)
                company_logo_url = request.build_absolute_uri(f"/media/{relative_path}")
            except Exception:
                company_logo_url = f"/media/{os.path.basename(logo_path)}"
        
        # Generate verification token for current timestamp
        signed_at = datetime.now().isoformat()
        verification_token = generate_verification_token(user.id, signed_at)
        
        # Build signature JSON data
        signature_data = {
            'success': True,
            'can_create_signature': can_create,
            'missing_fields': missing_fields,
            'signer_name': f"{user.name or ''} {user.surname or ''}".strip() or user.username,
            'employee_id': getattr(detail, 'employee_id', '') or '',
            'designation': user.designation or '',
            'department': user.department or '',
            'company_name': generator._get_company_name(user) or '',
            'company_logo_url': company_logo_url,
            'logo_source': logo_source,
            'signed_at': signed_at,
            'verification_token': verification_token,
            'template_version': '5.0-json',
            'user_id': user.id,
            'user_type': user.user_type,
            'admin_type': user.admin_type
        }
        
        # Store JSON data (no image) for audit
        if hasattr(detail, 'signature_template_data'):
            detail.signature_template_data = signature_data
            detail.save(update_fields=['signature_template_data'])
        
        return Response(signature_data)
        
    except Exception as e:
        logger.exception(f"Error getting signature JSON data for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to load signature data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_document_json(request):
    """Record document signing with JSON audit (no image storage)"""
    try:
        user = request.user
        
        # Get form context from request
        form_type = request.data.get('form_type', 'document')
        form_id = request.data.get('form_id', 0)
        context = request.data.get('context', 'signature')
        
        # Get or create detail record
        if user.user_type in ['adminuser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master']:
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
                'error': 'Name is required for signing'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate signing timestamp and verification token
        signed_at = datetime.now().isoformat()
        verification_token = generate_verification_token(user.id, signed_at, context)
        
        # Get client info
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Build signature audit data (JSON only)
        signature_audit = {
            'user_id': user.id,
            'signer_name': f"{user.name or ''} {user.surname or ''}".strip() or user.username,
            'employee_id': getattr(detail, 'employee_id', '') or '',
            'designation': user.designation or '',
            'department': user.department or '',
            'form_type': form_type,
            'form_id': form_id,
            'context': context,
            'signed_at': signed_at,
            'verification_token': verification_token,
            'ip_address': ip_address,
            'user_agent': user_agent[:200],  # Truncate user agent
            'template_version': '5.0-json'
        }
        
        # Store in signature_template_data for audit (reuse existing field)
        if hasattr(detail, 'signature_template_data'):
            # Keep existing data and add signing record
            existing_data = detail.signature_template_data or {}
            if 'signing_history' not in existing_data:
                existing_data['signing_history'] = []
            existing_data['signing_history'].append(signature_audit)
            existing_data['last_signed'] = signature_audit
            detail.signature_template_data = existing_data
            detail.save(update_fields=['signature_template_data'])
        
        logger.info(f"Document signed (JSON-only) by user {user.id} for {form_type}#{form_id}")
        
        return Response({
            'success': True,
            'message': 'Document signed successfully',
            'signature_data': signature_audit
        })
        
    except Exception as e:
        logger.exception(f"Error recording signature for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to record signature'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_signature_json(request):
    """Preview signature as JSON data (no image generation)"""
    try:
        user = request.user
        
        # Get detail record
        if user.user_type in ['adminuser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master']:
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            return Response({
                'success': False,
                'error': 'Unsupported user type'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get signature JSON data
        generator = SignatureTemplateGenerator()
        logo_file, logo_source, logo_path = generator.resolve_company_logo(user)
        
        # Build company logo URL
        company_logo_url = None
        if logo_file and hasattr(logo_file, 'url'):
            try:
                company_logo_url = request.build_absolute_uri(logo_file.url)
            except Exception:
                company_logo_url = logo_file.url  # Fallback to relative URL
        elif logo_path and os.path.exists(logo_path):
            try:
                relative_path = os.path.relpath(logo_path, settings.MEDIA_ROOT)
                company_logo_url = request.build_absolute_uri(f"/media/{relative_path}")
            except Exception:
                company_logo_url = f"/media/{os.path.basename(logo_path)}"
        
        # Preview data (current timestamp for preview)
        preview_data = {
            'success': True,
            'signer_name': f"{user.name or ''} {user.surname or ''}".strip() or user.username,
            'employee_id': getattr(detail, 'employee_id', '') or '',
            'designation': user.designation or '',
            'department': user.department or '',
            'company_name': generator._get_company_name(user) or '',
            'company_logo_url': company_logo_url,
            'signed_at': datetime.now().isoformat(),  # Preview timestamp
            'verification_token': 'PREVIEW',
            'template_version': '5.0-json',
            'is_preview': True
        }
        
        return Response(preview_data)
        
    except Exception as e:
        logger.exception(f"Error generating signature preview for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to generate preview'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Legacy endpoint compatibility (keep existing PNG behavior)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_template_legacy(request):
    """Legacy PNG preview endpoint (backward compatibility)"""
    try:
        user = request.user
        fresh = request.query_params.get('fresh') == '1'
        
        # Get detail record
        if user.user_type in ['adminuser']:
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type in ['projectadmin', 'master']:
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
        
        # Return existing template URL
        template_url = request.build_absolute_uri(detail.signature_template.url)
        return Response({
            'success': True,
            'template_url': template_url
        })
        
    except Exception as e:
        logger.exception(f"Error previewing legacy template for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Failed to preview template'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)