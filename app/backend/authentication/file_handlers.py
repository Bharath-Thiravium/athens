"""
Secure file upload handlers with path traversal protection
"""
import os
import mimetypes
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
from .security_utils import secure_filename, safe_join, validate_file_path


class SecureFileHandler:
    """Secure file upload handler with validation"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @classmethod
    def handle_upload(cls, uploaded_file, upload_path='uploads'):
        """Securely handle file upload with validation"""
        if not uploaded_file:
            raise ValidationError("No file provided")
        
        # Validate file size
        if uploaded_file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"File size exceeds {cls.MAX_FILE_SIZE} bytes")
        
        # Secure the filename
        filename = secure_filename(uploaded_file.name)
        
        # Validate file extension
        _, ext = os.path.splitext(filename.lower())
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(f"File type {ext} not allowed")
        
        # Create secure path
        secure_path = safe_join(settings.MEDIA_ROOT, upload_path, filename)
        
        # Validate the final path
        validate_file_path(secure_path)
        
        # Save file securely
        relative_path = os.path.join(upload_path, filename)
        saved_path = default_storage.save(relative_path, uploaded_file)
        
        return saved_path
    
    @classmethod
    def validate_file_access(cls, file_path):
        """Validate file access is within allowed directories"""
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        # Convert to absolute path and validate
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
        validate_file_path(abs_path)
        
        return abs_path