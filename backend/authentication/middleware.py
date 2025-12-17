"""
Security middleware for input validation and sanitization
"""
import re
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError


class SecurityMiddleware(MiddlewareMixin):
    """Middleware for security validation"""
    
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'\.\./',
        r'\\.\\.\\',
    ]
    
    def process_request(self, request):
        """Validate request for security threats"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Skip validation for admin detail updates (multipart form data)
                if request.content_type and 'multipart/form-data' in request.content_type:
                    # Only validate file uploads for multipart requests
                    if request.FILES:
                        for file_field, uploaded_file in request.FILES.items():
                            if not self._validate_file_upload(uploaded_file):
                                return JsonResponse({
                                    'error': 'Invalid file upload',
                                    'code': 'FILE_VALIDATION_ERROR'
                                }, status=400)
                    return None
                
                # Check for XSS patterns in JSON request data only
                if hasattr(request, 'body') and request.body:
                    body_str = request.body.decode('utf-8', errors='ignore')
                    if self._contains_dangerous_patterns(body_str):
                        return JsonResponse({
                            'error': 'Invalid input detected',
                            'code': 'SECURITY_VIOLATION'
                        }, status=400)
                            
            except Exception:
                # Don't block request on validation errors
                pass
        
        return None
    
    def _contains_dangerous_patterns(self, text):
        """Check if text contains dangerous patterns"""
        # Skip validation for multipart form data (file uploads)
        if 'multipart/form-data' in text or 'Content-Disposition: form-data' in text:
            return False
            
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _validate_file_upload(self, uploaded_file):
        """Validate uploaded file"""
        # Check file size (10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False
        
        # Check file extension
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        file_extension = uploaded_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return False
        
        return True