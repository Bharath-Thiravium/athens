from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import os
from django.conf import settings
from django.http import FileResponse

@login_required
@require_http_methods(["GET"])
def signature_preview(request):
    """Serve the user's signature template image"""
    try:
        user = request.user
        
        # Check if user has signature template
        if hasattr(user, 'userdetail') and user.userdetail.signature_template:
            template_path = user.userdetail.signature_template.path
        elif hasattr(user, 'admindetail') and user.admindetail.signature_template:
            template_path = user.admindetail.signature_template.path
        else:
            raise Http404("No signature template found")
        
        # Check if file exists
        if not os.path.exists(template_path):
            raise Http404("Template file not found")
        
        # Serve the image file
        return FileResponse(open(template_path, 'rb'), content_type='image/png')
            
    except Exception as e:
        raise Http404("Template not available")