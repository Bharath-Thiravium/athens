"""
Security utilities for safe file handling and input validation
"""
import os
import re
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError


def secure_filename(filename):
    """Sanitize filename to prevent path traversal"""
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    if not filename or filename in ('.', '..'):
        raise ValidationError("Invalid filename")
    
    return filename


def safe_join(base_path, *paths):
    """Safely join paths to prevent directory traversal"""
    base = Path(base_path).resolve()
    
    for path in paths:
        if not path:
            continue
        # Sanitize each path component
        path = secure_filename(str(path))
        base = base / path
    
    # Ensure the final path is within the base directory
    try:
        base.resolve().relative_to(Path(base_path).resolve())
    except ValueError:
        raise ValidationError("Path traversal attempt detected")
    
    return str(base)


def validate_file_path(file_path, allowed_base_paths=None):
    """Validate file path is within allowed directories"""
    if not allowed_base_paths:
        allowed_base_paths = [settings.MEDIA_ROOT]
    
    file_path = Path(file_path).resolve()
    
    for base_path in allowed_base_paths:
        try:
            file_path.relative_to(Path(base_path).resolve())
            return True
        except ValueError:
            continue
    
    raise ValidationError("File path not in allowed directories")


def sanitize_log_input(input_string):
    """Sanitize input for logging to prevent log injection"""
    if not input_string:
        return ""
    
    # Remove newlines and control characters
    sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', '', str(input_string))
    return sanitized[:500]  # Limit length