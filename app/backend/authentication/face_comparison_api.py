from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import tempfile
import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_faces_api(request):
    """
    Compare captured photo with reference photo for training attendance
    Uses strict face recognition with proper validation
    """
    captured_photo = request.FILES.get('captured_photo')
    reference_photo_url = request.data.get('reference_photo_url')
    
    if not captured_photo or not reference_photo_url:
        return Response({
            'error': 'Both captured_photo and reference_photo_url are required',
            'matched': False,
            'confidence': 0.0
        }, status=status.HTTP_400_BAD_REQUEST)
    
    temp_captured_path = None
    
    try:
        # Save captured photo temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in captured_photo.chunks():
                temp_file.write(chunk)
            temp_captured_path = temp_file.name
        
        # Get reference photo path from URL
        if reference_photo_url.startswith('/media/'):
            reference_path = reference_photo_url.replace('/media/', '')
            reference_full_path = default_storage.path(reference_path)
        else:
            # Handle full URLs
            reference_path = reference_photo_url.split('/media/')[-1]
            reference_full_path = default_storage.path(reference_path)
        
        # Validate file paths exist
        if not os.path.exists(reference_full_path):
            logger.error(f"Reference image not found: {reference_full_path}")
            return Response({
                'error': 'Reference image file not found',
                'matched': False,
                'confidence': 0.0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not os.path.exists(temp_captured_path):
            logger.error(f"Captured image not found: {temp_captured_path}")
            return Response({
                'error': 'Captured image file not found',
                'matched': False,
                'confidence': 0.0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the improved face recognition from shared module
        try:
            from shared.training_face_recognition import compare_training_faces
            
            # Open the captured photo as a file-like object
            with open(temp_captured_path, 'rb') as captured_file:
                # Use strict 70% threshold for training attendance
                face_result = compare_training_faces(reference_full_path, captured_file, confidence_threshold=0.70)
            
            logger.info(f"Face comparison API result - Match: {face_result['matched']}, Confidence: {face_result['confidence']:.3f}, Method: {face_result['method']}")
            
            # Return response with clear validation message
            if face_result['matched']:
                message = f"Face verified with {face_result['confidence']*100:.1f}% confidence"
            else:
                message = f"Face does not match. Confidence: {face_result['confidence']*100:.1f}%. {face_result['message']}"
            
            return Response({
                'matched': face_result['matched'],
                'confidence': face_result['confidence'],
                'message': message,
                'method': face_result['method'],
                'validation_details': {
                    'threshold_used': 0.70,
                    'confidence_percentage': f"{face_result['confidence']*100:.1f}%",
                    'result': 'MATCH' if face_result['matched'] else 'NO MATCH'
                }
            })
            
        except Exception as e:
            logger.error(f"Face comparison error: {str(e)}")
            return Response({
                'error': f'Face comparison failed: {str(e)}',
                'matched': False,
                'confidence': 0.0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response({
            'error': f'Face comparison API failed: {str(e)}',
            'matched': False,
            'confidence': 0.0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    finally:
        # Clean up temporary file
        if temp_captured_path and os.path.exists(temp_captured_path):
            try:
                os.unlink(temp_captured_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")