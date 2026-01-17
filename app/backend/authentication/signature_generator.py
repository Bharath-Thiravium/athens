from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.conf import settings
import os
import io
import logging

logger = logging.getLogger(__name__)

def generate_signature_image(user_data, logo_path=None):
    """Generate professional signature image with company logo background"""
    try:
        WIDTH, HEIGHT = 800, 200
        
        # Create base image
        image = Image.new('RGBA', (WIDTH, HEIGHT), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Add company logo background (50% transparency)
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert('RGBA')
                # Resize logo to fit background
                logo = logo.resize((300, 150), Image.Resampling.LANCZOS)
                # Set 50% transparency
                logo.putalpha(128)
                # Center logo
                logo_x = (WIDTH - 300) // 2
                logo_y = (HEIGHT - 150) // 2
                image.paste(logo, (logo_x, logo_y), logo)
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")
        
        # Use default font (no external font file needed)
        try:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Left side - Name and Employee ID
        left_x = 20
        draw.text((left_x, 40), user_data['full_name'], fill='black', font=font_large)
        if user_data.get('employee_id') and user_data['employee_id'] != 'Not set':
            draw.text((left_x, 70), f"Employee ID: {user_data['employee_id']}", fill='black', font=font_small)
        
        # Right side - Digital signature info
        right_x = 450
        draw.text((right_x, 30), f"Digitally signed by", fill='black', font=font_small)
        draw.text((right_x, 50), user_data['full_name'], fill='black', font=font_large)
        if user_data.get('designation') and user_data['designation'] != 'Not set':
            draw.text((right_x, 80), user_data['designation'], fill='black', font=font_small)
        if user_data.get('company_name') and user_data['company_name'] != 'Not set':
            draw.text((right_x, 100), user_data['company_name'], fill='black', font=font_small)
        
        # Save to BytesIO
        img_io = io.BytesIO()
        image.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        return ContentFile(img_io.getvalue(), name=f'signature_template_{user_data["user_id"]}.png')
        
    except Exception as e:
        logger.error(f"Error generating signature image: {e}")
        raise

def create_user_signature_template(user_detail):
    """Create signature template for UserDetail"""
    try:
        user = user_detail.user
        logger.info(f"Generating signature for user {user.id} - {user.username}")
        
        user_data = {
            'user_id': user.id,
            'full_name': f"{user.name} {user.surname}" if user.name and user.surname else user.name or user.username,
            'designation': user.designation or 'Not set',
            'company_name': user.company_name or 'Not set',
            'employee_id': user_detail.employee_id or 'Not set'
        }
        
        # Get company logo path if available
        logo_path = None
        
        # For EPCuser, inherit from master's CompanyDetail
        if user.admin_type == 'epcuser':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        logo_path = company_detail.company_logo.path
            except Exception as e:
                logger.warning(f"Failed to get master company logo: {e}")
        
        # Fallback: check user's own company detail
        if not logo_path and hasattr(user, 'company_detail') and user.company_detail.company_logo:
            logo_path = user.company_detail.company_logo.path
        
        # Generate signature image
        signature_file = generate_signature_image(user_data, logo_path)
        
        # CRITICAL FIX: Use Django's save method for ImageField
        user_detail.signature_template.save(
            signature_file.name,
            signature_file,
            save=True
        )
        
        logger.info(f"Signature template created successfully for user {user.username}")
        
    except Exception as e:
        logger.error(f"Error creating user signature template for {user.username}: {e}", exc_info=True)
        raise

def create_admin_signature_template(admin_detail):
    """Create signature template for AdminDetail"""
    try:
        user = admin_detail.user
        logger.info(f"Generating admin signature for user {user.id} - {user.username}")
        
        user_data = {
            'user_id': user.id,
            'full_name': user.name or user.username,
            'designation': user.designation or 'Administrator',
            'company_name': user.company_name or 'Not set',
            'employee_id': 'Admin'
        }
        
        # Get admin logo path if available
        logo_path = None
        
        # For EPC project admins, inherit from master's CompanyDetail
        if user.admin_type == 'epc':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        logo_path = company_detail.company_logo.path
            except Exception as e:
                logger.warning(f"Failed to get master company logo: {e}")
        
        # Fallback: use admin's own logo
        if not logo_path and admin_detail.logo:
            logo_path = admin_detail.logo.path
        
        # Generate signature image
        signature_file = generate_signature_image(user_data, logo_path)
        
        # CRITICAL FIX: Use Django's save method for ImageField
        admin_detail.signature_template.save(
            signature_file.name,
            signature_file,
            save=True
        )
        
        logger.info(f"Admin signature template created successfully for user {user.username}")
        
    except Exception as e:
        logger.error(f"Error creating admin signature template for {user.username}: {e}", exc_info=True)
        raise