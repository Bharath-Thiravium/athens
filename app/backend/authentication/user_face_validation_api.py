from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_user_self_face(request):
    """
    Validate that the captured photo matches the logged-in user's registered face
    This ensures attendance is only marked for the correct user
    """
    captured_photo = request.FILES.get('captured_photo')
    
    if not captured_photo:
        return Response({
            'error': 'Captured photo is required',
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
        
        # Use the user validation function from shared module
        try:
            from shared.training_face_recognition import validate_user_face_attendance
            
            # Convert file to base64 for the validation function
            with open(temp_captured_path, 'rb') as f:
                import base64
                image_data = base64.b64encode(f.read()).decode('utf-8')
                attendance_photo = f"data:image/jpeg;base64,{image_data}"
            
            # Validate against logged-in user's photo with strict 70% threshold
            face_result = validate_user_face_attendance(request.user, attendance_photo, confidence_threshold=0.70)
            
            logger.info(f"User self-validation for {request.user.username} - Match: {face_result['matched']}, Confidence: {face_result['confidence']:.3f}")
            
            # Return response with clear validation message
            if face_result['matched']:
                message = f"Identity verified for {request.user.username} with {face_result['confidence']*100:.1f}% confidence"
            else:
                message = f"Identity verification failed for {request.user.username}. {face_result['message']}"
            
            return Response({
                'matched': face_result['matched'],
                'confidence': face_result['confidence'],
                'message': message,
                'method': face_result['method'],
                'user_validation': True,
                'validated_user': request.user.username,
                'validation_details': {
                    'threshold_used': 0.70,
                    'confidence_percentage': f"{face_result['confidence']*100:.1f}%",
                    'result': 'VERIFIED' if face_result['matched'] else 'REJECTED'
                }
            })
            
        except Exception as e:
            logger.error(f"User self-validation error: {str(e)}")
            return Response({
                'error': f'Face validation failed: {str(e)}',
                'matched': False,
                'confidence': 0.0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return Response({
            'error': f'Face validation API failed: {str(e)}',
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