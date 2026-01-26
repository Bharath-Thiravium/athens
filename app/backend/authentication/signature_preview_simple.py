import os
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserDetail, AdminDetail
from .signature_template_generator_new import SignatureTemplateGenerator
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signature_template_preview_simple(request):
    """Simple template preview that works"""
    try:
        user = request.user

        def _render_preview(detail):
            generator = SignatureTemplateGenerator(logo_opacity=0.5)
            template_file, _ = generator.create_signature_template(detail)
            template_file.seek(0)
            logger.info("Signature preview generated for user %s", user.id)
            response = HttpResponse(template_file.read(), content_type='image/png')
            response['Cache-Control'] = 'no-store'
            return response

        fresh = request.query_params.get('fresh') == '1'

        # Resolve detail for current user
        if user.user_type == 'adminuser':
            detail, created = UserDetail.objects.get_or_create(user=user)
        elif user.user_type == 'projectadmin':
            detail, created = AdminDetail.objects.get_or_create(user=user)
        elif user.user_type == 'master':
            detail, created = AdminDetail.objects.get_or_create(user=user)
        else:
            logger.warning("Preview requested for unsupported user_type=%s user=%s", user.user_type, user.id)
            return Response({
                'success': False,
                'error': 'No template found'
            }, status=404)

        # Always generate fresh preview when requested
        if fresh:
            logger.info("Fresh preview requested for user %s", user.id)
            return _render_preview(detail)

        # Check if template exists and is readable
        if not getattr(detail, 'signature_template', None):
            logger.info("No existing template for user %s, generating new one", user.id)
            return _render_preview(detail)

        template_path = detail.signature_template.path
        if not os.path.exists(template_path):
            logger.warning("Signature template file missing at %s for user %s", template_path, user.id)
            return _render_preview(detail)

        # Return existing template URL
        template_url = request.build_absolute_uri(detail.signature_template.url)
        return Response({
            'success': True,
            'template_url': template_url
        })

    except Exception as e:
        logger.exception("Preview error: %s", str(e))
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
