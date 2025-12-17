"""
Secure Authentication Views
Handles both legacy and secure login formats for backward compatibility
"""

import base64
import json
import hashlib
import time
import logging
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser
from .serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)

class SecureCompatibleLoginView(View):
    """
    Backward-compatible login view that handles both:
    1. Legacy format: {"username": "user", "password": "pass"}
    2. Secure format: {"credentials": "encoded", "timestamp": 123, "hash": "abc", ...}
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Check if this is the new secure format
            if 'credentials' in data and 'timestamp' in data and 'hash' in data:
                return self._handle_secure_login(request, data)
            else:
                # Handle legacy format for backward compatibility
                return self._handle_legacy_login(request, data)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)
    
    def _handle_secure_login(self, request, data):
        """Handle the new secure login format"""
        try:
            # Security Check 1: Validate required fields
            required_fields = ['credentials', 'timestamp', 'hash', 'clientId']
            if not all(field in data for field in required_fields):
                return JsonResponse({
                    'error': 'Invalid request format'
                }, status=400)
            
            # Security Check 2: Timestamp validation (prevent replay attacks)
            timestamp = data.get('timestamp')
            current_time = int(time.time() * 1000)  # Current time in milliseconds
            time_diff = abs(current_time - timestamp)
            
            # Allow requests within 5 minutes
            if time_diff > 5 * 60 * 1000:
                logger.warning(f"Login attempt with old timestamp: {time_diff}ms difference")
                return JsonResponse({
                    'error': 'Request expired'
                }, status=400)
            
            # Security Check 3: Rate limiting per client
            client_id = data.get('clientId')
            rate_limit_key = f"login_attempts_{client_id}"
            attempts = cache.get(rate_limit_key, 0)
            
            max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
            if attempts >= max_attempts:
                return JsonResponse({
                    'error': 'Too many login attempts. Please try again later.'
                }, status=429)
            
            # Security Check 4: Decode credentials
            try:
                encoded_credentials = data.get('credentials')
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
            except Exception as e:
                logger.error(f"Failed to decode credentials: {str(e)}")
                cache.set(rate_limit_key, attempts + 1, timeout=900)  # 15 minutes
                return JsonResponse({
                    'error': 'Invalid credentials format'
                }, status=400)
            
            # Security Check 5: Validate hash integrity
            expected_hash = hashlib.sha256(
                f"{username}{timestamp}{client_id}".encode()
            ).hexdigest()
            
            if data.get('hash') != expected_hash:
                logger.warning(f"Hash mismatch for user: {username}")
                cache.set(rate_limit_key, attempts + 1, timeout=900)
                return JsonResponse({
                    'error': 'Request integrity check failed'
                }, status=400)
            
            # Security Check 6: Input sanitization
            username = username.strip()[:150]  # Limit length
            if not username or not password:
                cache.set(rate_limit_key, attempts + 1, timeout=900)
                return JsonResponse({
                    'error': 'Username and password are required'
                }, status=400)
            
            # Authenticate user
            return self._authenticate_user(request, username, password, client_id, rate_limit_key, attempts)
            
        except Exception as e:
            logger.error(f"Secure login error: {str(e)}")
            return JsonResponse({
                'error': 'Authentication failed'
            }, status=500)
    
    def _handle_legacy_login(self, request, data):
        """Handle the legacy login format for backward compatibility"""
        try:
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return JsonResponse({
                    'error': 'Username and password are required'
                }, status=400)
            
            # Use IP-based rate limiting for legacy requests
            client_ip = self._get_client_ip(request)
            rate_limit_key = f"login_attempts_legacy_{client_ip}"
            attempts = cache.get(rate_limit_key, 0)
            
            # Authenticate user
            return self._authenticate_user(request, username, password, client_ip, rate_limit_key, attempts)
            
        except Exception as e:
            logger.error(f"Legacy login error: {str(e)}")
            return JsonResponse({
                'error': 'Authentication failed'
            }, status=500)
    
    def _authenticate_user(self, request, username, password, client_id, rate_limit_key, attempts):
        """Common authentication logic"""
        try:
            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    # Clear rate limiting on successful login
                    cache.delete(rate_limit_key)
                    
                    # Log successful login
                    logger.info(f"Successful login for user: {username}")
                    
                    # Generate tokens using your existing logic
                    refresh = RefreshToken.for_user(user)
                    access = refresh.access_token
                    
                    # Get user data (matching your existing CustomTokenObtainPairSerializer format)
                    # Replicate the exact logic from CustomTokenObtainPairSerializer
                    if user.user_type == 'projectadmin':
                        # Handle master admin specially
                        if user.admin_type == 'master':
                            usertype = 'master'
                            username = user.username
                        # For multiple contractor admins, append index to usertype if admin_type is contractor
                        elif user.admin_type == 'contractor':
                            # Find index of this contractor admin among all contractor admins in the project
                            from .models import CustomUser
                            if user.project:  # Only if user has a project
                                contractor_admins = CustomUser.objects.filter(
                                    project=user.project,
                                    user_type='projectadmin',
                                    admin_type='contractor'
                                ).order_by('id')
                                index = None
                                for i, admin in enumerate(contractor_admins, start=1):
                                    if admin.pk == user.pk:
                                        index = i
                                        break
                                if index:
                                    usertype = f'contractor{index}'
                                else:
                                    usertype = user.admin_type
                            else:
                                usertype = user.admin_type
                            username = user.username
                        else:
                            usertype = user.admin_type
                            username = user.username
                    elif user.user_type == 'adminuser':
                        usertype = user.admin_type
                        username = user.email
                    elif hasattr(user, 'is_staff') and user.is_staff:
                        usertype = 'staff'
                        username = getattr(user, 'username', None)
                    else:
                        usertype = 'user'
                        username = getattr(user, 'username', None)

                    user_data = {
                        'access': str(access),
                        'refresh': str(refresh),
                        'username': username,
                        'userId': user.id,
                        'user_id': user.id,  # For backward compatibility
                        'usertype': usertype,
                        'django_user_type': user.user_type,
                        'isPasswordResetRequired': getattr(user, 'is_password_reset_required', False),
                        'grade': getattr(user, 'grade', None),
                        'project_id': user.project.id if user.project else None,
                    }
                    
                    return JsonResponse(user_data)
                else:
                    # Increment rate limiting for inactive account
                    cache.set(rate_limit_key, attempts + 1, timeout=900)  # 15 minutes
                    return JsonResponse({
                        'detail': 'Account is disabled'  # Match DRF format
                    }, status=401)
            else:
                # Increment rate limiting for failed login
                cache.set(rate_limit_key, attempts + 1, timeout=900)  # 15 minutes
                logger.warning(f"Failed login attempt for user: {username}")
                return JsonResponse({
                    'detail': 'Invalid credentials'  # Match DRF format
                }, status=401)
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            cache.set(rate_limit_key, attempts + 1, timeout=900)
            return JsonResponse({
                'detail': 'Authentication failed'
            }, status=500)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# For backward compatibility, you can also create a DRF-compatible view
from rest_framework.views import APIView
from rest_framework.response import Response

class SecureCompatibleLoginAPIView(APIView):
    """
    DRF-compatible version of the secure login view
    """
    permission_classes = []  # Allow unauthenticated access
    
    def post(self, request):
        # Use the same logic as the Django view
        django_view = SecureCompatibleLoginView()
        django_response = django_view.post(request)
        
        # Convert Django JsonResponse to DRF Response
        if hasattr(django_response, 'content'):
            try:
                content = json.loads(django_response.content.decode('utf-8'))
                return Response(content, status=django_response.status_code)
            except:
                return Response({'error': 'Internal server error'}, status=500)
        
        return Response({'error': 'Internal server error'}, status=500)
