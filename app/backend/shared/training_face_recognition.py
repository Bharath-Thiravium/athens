"""
Shared face recognition utility for training attendance modules
Provides consistent face recognition functionality across Induction Training, Job Training, and Toolbox Talk
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import os
import base64

logger = logging.getLogger(__name__)

# Try to import face_recognition, use fallback if not available
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    logger.info("face_recognition library loaded successfully for training modules")
except (ImportError, SystemExit, Exception) as e:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning(f"face_recognition library not available for training modules: {e}, using basic face detection fallback")

def compare_training_faces(known_image_path, unknown_image_data, confidence_threshold=0.65):
    """
    Compare faces for training attendance with 65% confidence threshold
    
    Args:
        known_image_path: Path to stored profile photo
        unknown_image_data: Base64 encoded image data or file path
        confidence_threshold: Minimum confidence for match (default 0.65)
    
    Returns:
        dict: {
            'matched': bool,
            'confidence': float,
            'message': str,
            'method': str
        }
    """
    try:
        # Check if known image exists
        if not os.path.exists(known_image_path):
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'Reference photo not found',
                'method': 'error'
            }
        
        # Process unknown image data
        if isinstance(unknown_image_data, str):
            # Handle base64 encoded image
            if unknown_image_data.startswith('data:image'):
                # Extract base64 data
                format_part, imgstr = unknown_image_data.split(';base64,')
                image_data = base64.b64decode(imgstr)
            else:
                # Assume it's already base64
                image_data = base64.b64decode(unknown_image_data)
            
            unknown_image_file = BytesIO(image_data)
        else:
            unknown_image_file = unknown_image_data
        
        # Use advanced face recognition if available
        if FACE_RECOGNITION_AVAILABLE:
            return compare_training_faces_advanced(known_image_path, unknown_image_file, confidence_threshold)
        else:
            return compare_training_faces_basic(known_image_path, unknown_image_file)
            
    except Exception as e:
        logger.error(f"Face comparison error: {e}")
        return {
            'matched': False,
            'confidence': 0.0,
            'message': f'Face comparison failed: {str(e)}',
            'method': 'error'
        }

def compare_training_faces_advanced(known_image_path, unknown_image_file, confidence_threshold=0.65):
    """
    Advanced face recognition using face_recognition library
    """
    try:
        # Load and preprocess known image
        known_image = face_recognition.load_image_file(known_image_path)
        known_image = preprocess_training_image(known_image)
        
        # Load and preprocess unknown image
        unknown_pil_image = Image.open(unknown_image_file)
        unknown_image = np.array(unknown_pil_image)
        unknown_image = preprocess_training_image(unknown_image)
        
        # Get face encodings
        known_face_encodings = face_recognition.face_encodings(known_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image)
        
        if len(known_face_encodings) == 0:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'No face detected in profile photo',
                'method': 'advanced'
            }
        
        if len(unknown_face_encodings) == 0:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'No face detected in attendance photo',
                'method': 'advanced'
            }
        
        # Find best match among all detected faces
        best_confidence = 0.0
        for k_enc in known_face_encodings:
            for u_enc in unknown_face_encodings:
                distance = face_recognition.face_distance([k_enc], u_enc)[0]
                confidence = max(0.0, 1.0 - distance)
                if confidence > best_confidence:
                    best_confidence = confidence
        
        # Apply confidence threshold
        matched = best_confidence >= confidence_threshold
        
        logger.info(f"Training face recognition - Confidence: {best_confidence:.3f} ({best_confidence*100:.1f}%), Result: {'MATCH' if matched else 'NO MATCH'}")
        
        return {
            'matched': matched,
            'confidence': best_confidence,
            'message': f'Face recognition completed with {best_confidence*100:.1f}% confidence',
            'method': 'advanced'
        }
        
    except Exception as e:
        logger.error(f"Advanced face recognition error: {e}")
        return {
            'matched': False,
            'confidence': 0.0,
            'message': f'Advanced face recognition failed: {str(e)}',
            'method': 'advanced_error'
        }

def compare_training_faces_basic(known_image_path, unknown_image_file):
    """
    Strict basic face detection that actually compares faces when face_recognition is not available
    """
    try:
        logger.warning("Using basic face detection for training attendance - install face_recognition for better accuracy")
        
        # Load known image
        known_image = cv2.imread(known_image_path)
        if known_image is None:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'Could not load profile photo',
                'method': 'basic'
            }
        
        # Load unknown image
        unknown_image_file.seek(0)
        image_data = unknown_image_file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        unknown_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if unknown_image is None:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'Could not decode attendance photo',
                'method': 'basic'
            }
        
        # Initialize face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale and preprocess
        known_gray = cv2.cvtColor(known_image, cv2.COLOR_BGR2GRAY)
        unknown_gray = cv2.cvtColor(unknown_image, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better comparison
        known_gray = cv2.equalizeHist(known_gray)
        unknown_gray = cv2.equalizeHist(unknown_gray)
        
        # Detect faces with strict parameters
        known_faces = face_cascade.detectMultiScale(
            known_gray, 
            scaleFactor=1.05, 
            minNeighbors=6, 
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        unknown_faces = face_cascade.detectMultiScale(
            unknown_gray, 
            scaleFactor=1.05, 
            minNeighbors=6, 
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        logger.info(f"Basic face detection - Known faces: {len(known_faces)}, Unknown faces: {len(unknown_faces)}")
        
        # Require exactly one face in both images for security
        if len(known_faces) != 1 or len(unknown_faces) != 1:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': f'Face validation failed - Expected 1 face in each image, found {len(known_faces)} and {len(unknown_faces)}',
                'method': 'basic'
            }
        
        # Extract face regions
        known_face = known_faces[0]
        unknown_face = unknown_faces[0]
        
        # Extract face regions with padding
        kx, ky, kw, kh = known_face
        ux, uy, uw, uh = unknown_face
        
        # Add padding (10% of face size)
        k_pad = max(5, int(0.1 * min(kw, kh)))
        u_pad = max(5, int(0.1 * min(uw, uh)))
        
        # Extract face regions with bounds checking
        known_face_region = known_gray[
            max(0, ky-k_pad):min(known_gray.shape[0], ky+kh+k_pad),
            max(0, kx-k_pad):min(known_gray.shape[1], kx+kw+k_pad)
        ]
        unknown_face_region = unknown_gray[
            max(0, uy-u_pad):min(unknown_gray.shape[0], uy+uh+u_pad),
            max(0, ux-u_pad):min(unknown_gray.shape[1], ux+uw+u_pad)
        ]
        
        # Resize both face regions to same size for comparison
        target_size = (100, 100)
        known_face_resized = cv2.resize(known_face_region, target_size)
        unknown_face_resized = cv2.resize(unknown_face_region, target_size)
        
        # Calculate multiple similarity metrics
        
        # 1. Template matching
        template_result = cv2.matchTemplate(known_face_resized, unknown_face_resized, cv2.TM_CCOEFF_NORMED)
        template_score = template_result[0][0]
        
        # 2. Histogram comparison
        known_hist = cv2.calcHist([known_face_resized], [0], None, [256], [0, 256])
        unknown_hist = cv2.calcHist([unknown_face_resized], [0], None, [256], [0, 256])
        hist_correlation = cv2.compareHist(known_hist, unknown_hist, cv2.HISTCMP_CORREL)
        
        # 3. Structural similarity (simplified)
        diff = cv2.absdiff(known_face_resized, unknown_face_resized)
        structural_similarity = 1.0 - (np.mean(diff) / 255.0)
        
        # 4. Face size and position similarity
        size_similarity = min(kw*kh, uw*uh) / max(kw*kh, uw*uh)
        
        # Combine metrics with weights
        combined_score = (
            template_score * 0.4 +
            hist_correlation * 0.3 +
            structural_similarity * 0.2 +
            size_similarity * 0.1
        )
        
        # Apply very strict threshold for basic detection to prevent false positives
        confidence_threshold = 0.85  # 85% threshold for basic detection (very strict)
        matched = combined_score >= confidence_threshold
        
        # Additional validation: reject if any individual metric is too low
        if matched:
            # All metrics must meet minimum thresholds
            if (template_score < 0.6 or 
                hist_correlation < 0.5 or 
                structural_similarity < 0.7 or 
                size_similarity < 0.4):
                matched = False
                logger.info("Face match rejected due to low individual metric scores")
        
        logger.info(f"Basic face comparison metrics:")
        logger.info(f"  - Template matching: {template_score:.3f}")
        logger.info(f"  - Histogram correlation: {hist_correlation:.3f}")
        logger.info(f"  - Structural similarity: {structural_similarity:.3f}")
        logger.info(f"  - Size similarity: {size_similarity:.3f}")
        logger.info(f"  - Combined score: {combined_score:.3f}")
        logger.info(f"  - Result: {'MATCH' if matched else 'NO MATCH'}")
        
        return {
            'matched': matched,
            'confidence': combined_score,
            'message': f'Basic face comparison completed with {combined_score*100:.1f}% confidence',
            'method': 'basic'
        }
            
    except Exception as e:
        logger.error(f"Basic face detection error: {e}")
        return {
            'matched': False,
            'confidence': 0.0,
            'message': f'Basic face detection failed: {str(e)}',
            'method': 'basic_error'
        }

def preprocess_training_image(image_array):
    """
    Consistent preprocessing for training attendance images
    """
    try:
        # Ensure RGB format
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            processed = image_array.copy()
        else:
            processed = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        
        # Normalize brightness and contrast
        gray = cv2.cvtColor(processed, cv2.COLOR_RGB2GRAY)
        
        # Adaptive histogram equalization for better lighting consistency
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
        
        # Slight denoising
        enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        return enhanced
    except Exception as e:
        logger.warning(f"Training image preprocessing failed: {e}, using original")
        return image_array

def get_logged_in_user_photo_path(request_user):
    """
    Get the logged-in user's photo path for face recognition validation
    
    Args:
        request_user: The authenticated user from the request
    
    Returns:
        str: Path to user's photo file or None if not found
    """
    try:
        from authentication.models import UserDetail, AdminDetail
        
        # Try UserDetail first
        try:
            user_detail = UserDetail.objects.get(user=request_user)
            if user_detail.photo and os.path.exists(user_detail.photo.path):
                return user_detail.photo.path
        except UserDetail.DoesNotExist:
            pass
        
        # Try AdminDetail
        try:
            admin_detail = AdminDetail.objects.get(user=request_user)
            if admin_detail.photo and os.path.exists(admin_detail.photo.path):
                return admin_detail.photo.path
        except AdminDetail.DoesNotExist:
            pass
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting logged-in user photo path: {e}")
        return None

def validate_user_face_attendance(request_user, attendance_photo, confidence_threshold=0.70):
    """
    Validate that the attendance photo matches the logged-in user's registered face
    
    Args:
        request_user: The authenticated user from the request
        attendance_photo: Base64 encoded attendance photo
        confidence_threshold: Minimum confidence for match (default 0.70)
    
    Returns:
        dict: Validation result with matched status, confidence, and message
    """
    try:
        # Get the logged-in user's photo path
        user_photo_path = get_logged_in_user_photo_path(request_user)
        
        if not user_photo_path:
            return {
                'matched': False,
                'confidence': 0.0,
                'message': 'No registered photo found for the logged-in user. Please update your profile photo.',
                'method': 'validation_error'
            }
        
        # Perform face comparison
        result = compare_training_faces(user_photo_path, attendance_photo, confidence_threshold)
        
        # Add user validation context
        if result['matched']:
            result['message'] = f"Face verified for user {request_user.username} with {result['confidence']*100:.1f}% confidence"
        else:
            result['message'] = f"Face does not match registered photo for user {request_user.username}. Attendance not marked."
        
        logger.info(f"User face validation for {request_user.username}: {'MATCH' if result['matched'] else 'NO MATCH'} ({result['confidence']*100:.1f}%)")
        
        return result
        
    except Exception as e:
        logger.error(f"User face validation error: {e}")
        return {
            'matched': False,
            'confidence': 0.0,
            'message': f'Face validation failed: {str(e)}',
            'method': 'validation_error'
        }
def get_participant_photo_path(participant_type, participant_id):
    """
    Get photo path for a participant (worker or user)
    
    Args:
        participant_type: 'worker' or 'user'
        participant_id: ID of the participant
    
    Returns:
        str: Path to photo file or None if not found
    """
    try:
        if participant_type == 'worker':
            from worker.models import Worker
            worker = Worker.objects.get(id=participant_id)
            if worker.photo and os.path.exists(worker.photo.path):
                return worker.photo.path
        
        elif participant_type == 'user':
            from django.contrib.auth import get_user_model
            from authentication.models import UserDetail, AdminDetail
            
            User = get_user_model()
            user = User.objects.get(id=participant_id)
            
            # Try UserDetail first
            try:
                user_detail = UserDetail.objects.get(user=user)
                if user_detail.photo and os.path.exists(user_detail.photo.path):
                    return user_detail.photo.path
            except UserDetail.DoesNotExist:
                pass
            
            # Try AdminDetail
            try:
                admin_detail = AdminDetail.objects.get(user=user)
                if admin_detail.photo and os.path.exists(admin_detail.photo.path):
                    return admin_detail.photo.path
            except AdminDetail.DoesNotExist:
                pass
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting participant photo path: {e}")
        return None