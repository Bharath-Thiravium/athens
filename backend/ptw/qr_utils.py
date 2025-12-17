try:
    import qrcode
except ImportError:
    qrcode = None
import base64
from io import BytesIO
from django.conf import settings
import json

def generate_permit_qr_code(permit):
    """Generate QR code for permit that contains a direct URL"""
    
    if qrcode is None:
        return None
    
    # Create the mobile-friendly URL
    base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')
    permit_url = f"{base_url}/mobile/permit/{permit.id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(permit_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_permit_qr_data(permit):
    """Generate QR code data string for permit"""
    qr_data = {
        'id': permit.id,
        'number': permit.permit_number,
        'type': permit.permit_type.category if permit.permit_type else '',
        'location': permit.location,
        'status': permit.status,
        'url': f"{getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')}/mobile/permit/{permit.id}"
    }
    return base64.b64encode(json.dumps(qr_data).encode()).decode()