from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deprecated_signature_generate(request):
    """
    Deprecated signature generation endpoint.
    Signatures are now JSON-only. Use /api/v1/ptw/permits/{id}/add_signature/ instead.
    """
    return Response(
        {
            'error': 'Deprecated. Signatures are JSON-only. Use /api/v1/ptw/permits/{id}/add_signature/.',
            'code': 'ENDPOINT_DEPRECATED',
            'migration_guide': {
                'old_endpoint': '/authentication/signature/generate/',
                'new_endpoint': '/api/v1/ptw/permits/{permit_id}/add_signature/',
                'new_format': 'JSON stroke data instead of PNG images'
            }
        },
        status=status.HTTP_410_GONE
    )