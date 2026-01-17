"""
Digital Signature Template Generator
Creates professional signature templates with company logo, user details, and dynamic date/time
"""

import os
import io
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import datetime
import json


class SignatureTemplateGenerator:
    """
    Generates digital signature templates with company branding
    """
    
    def __init__(self, logo_opacity=0.5):
        # Fixed canvas size as per requirements
        self.template_width = 800   # Fixed canvas width
        self.template_height = 200  # Fixed canvas height
        self.logo_max_width = 80
        self.logo_max_height = 60
        self.logo_opacity = logo_opacity  # Configurable logo transparency (0.0 to 1.0)
        
        # Layout zones as per requirements
        self.left_zone_x = 20
        self.center_zone_x = self.template_width // 2  # Horizontally centered
        self.right_zone_x = self.template_width - 350  # Right zone
        
    def create_signature_template(self, user_detail):
        """
        Create a signature template for a user in Adobe DSC style

        Args:
            user_detail: UserDetail instance

        Returns:
            tuple: (template_image_file, template_data_dict)
        """
        # Create base image with white background
        img = Image.new('RGBA', (self.template_width, self.template_height), (255, 255, 255, 255))
        
        # Load fonts with proper sizing for 800x200 canvas
        try:
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            detail_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            name_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
        
        # Colors
        text_color = (0, 0, 0)  # Black text
        
        # User's full name
        full_name = f"{user_detail.user.name or user_detail.user.username} {user_detail.user.surname or ''}".strip()
        if not full_name or full_name == user_detail.user.username:
            full_name = user_detail.user.username
        
        # Add company logo in CENTER ZONE (horizontally centered)
        company_logo = self._get_company_logo(user_detail.user)
        if company_logo:
            try:
                logo_path = company_logo.path
                if os.path.exists(logo_path):
                    logo = Image.open(logo_path)
                    # Resize logo to fit center zone
                    logo.thumbnail((self.logo_max_width, self.logo_max_height), Image.Resampling.LANCZOS)
                    
                    # Create logo with 50% opacity as required
                    logo_rgba = logo.convert('RGBA')
                    alpha = logo_rgba.split()[-1]
                    alpha = alpha.point(lambda p: int(p * 0.5))  # 50% opacity as required
                    logo_rgba.putalpha(alpha)
                    
                    # Position in CENTER ZONE (horizontally centered)
                    logo_x = self.center_zone_x - (logo.width // 2)
                    logo_y = (self.template_height - logo.height) // 2
                    
                    # Paste logo in center zone
                    img.paste(logo_rgba, (logo_x, logo_y), logo_rgba)
            except Exception as e:
                pass
        
        draw = ImageDraw.Draw(img)
        
        # LEFT ZONE: User name and Employee ID
        left_y = 40  # Starting Y position
        
        # Name in LEFT ZONE
        draw.text((self.left_zone_x, left_y), full_name, font=name_font, fill=text_color)
        
        # Employee ID in LEFT ZONE (below name)
        employee_id = None
        try:
            if hasattr(user_detail, 'employee_id') and user_detail.employee_id:
                employee_id = user_detail.employee_id
        except:
            pass
            
        if employee_id:
            left_y += 35
            draw.text((self.left_zone_x, left_y), f"Employee ID: {employee_id}", font=detail_font, fill=(102, 102, 102))
        
        # RIGHT ZONE: Digital signature text, designation, company
        right_y = 40  # Starting Y position
        
        # "Digitally signed by <Name>" in RIGHT ZONE
        draw.text((self.right_zone_x, right_y), f"Digitally signed by {full_name}", font=detail_font, fill=text_color)
        right_y += 25
        
        # Designation in RIGHT ZONE
        if user_detail.user.designation:
            draw.text((self.right_zone_x, right_y), user_detail.user.designation, font=detail_font, fill=(102, 102, 102))
            right_y += 25
        
        # Company name in RIGHT ZONE
        company_name = self._get_company_name(user_detail.user)
        if company_name:
            draw.text((self.right_zone_x, right_y), company_name, font=detail_font, fill=(136, 136, 136))
            right_y += 25
        
        # Date placeholder in RIGHT ZONE
        draw.text((self.right_zone_x, right_y), "Date: [TO_BE_FILLED]", font=detail_font, fill=(51, 51, 51))
        
        # Convert back to RGB
        img = img.convert('RGB')
        
        # Save template to memory
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        # Create template data with versioned filename
        employee_id = getattr(user_detail, 'employee_id', '') or ''
        template_data = {
            'user_id': user_detail.user.id,
            'full_name': full_name,
            'designation': user_detail.user.designation or '',
            'employee_id': employee_id,
            'company_name': self._get_company_name(user_detail.user),
            'template_created_at': datetime.now().isoformat(),
            'template_version': '4.0'  # Updated version for center-aligned layout
        }
        
        # Create Django file with versioned filename
        filename = f"signature_template_v4_{user_detail.user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        template_file = ContentFile(img_io.getvalue(), name=filename)
        
        return template_file, template_data

    def create_admin_signature_template(self, admin_detail):
        """
        Create a signature template for an admin in Adobe DSC style

        Args:
            admin_detail: AdminDetail instance

        Returns:
            tuple: (ContentFile, template_data_dict)
        """
        user = admin_detail.user

        # Get user information
        full_name = f"{user.name or ''} {user.surname or ''}".strip()
        if not full_name:
            full_name = user.username

        # Create image with white background
        img = Image.new('RGBA', (self.template_width, self.template_height), (255, 255, 255, 255))

        # Load fonts with proper sizing for 800x200 canvas
        try:
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            detail_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            name_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()

        # Colors
        text_color = (0, 0, 0)  # Black text

        # Add company logo in CENTER ZONE (horizontally centered)
        company_logo = self._get_company_logo(user)
        if company_logo:
            try:
                logo_img = Image.open(company_logo.path)
                # Resize logo to fit center zone
                logo_img.thumbnail((self.logo_max_width, self.logo_max_height), Image.Resampling.LANCZOS)
                
                # Create logo with 50% opacity as required
                logo_rgba = logo_img.convert('RGBA')
                alpha = logo_rgba.split()[-1]
                alpha = alpha.point(lambda p: int(p * 0.5))  # 50% opacity as required
                logo_rgba.putalpha(alpha)
                
                # Position in CENTER ZONE (horizontally centered)
                logo_x = self.center_zone_x - (logo_img.width // 2)
                logo_y = (self.template_height - logo_img.height) // 2
                
                # Paste logo in center zone
                img.paste(logo_rgba, (logo_x, logo_y), logo_rgba)
            except Exception as e:
                pass

        draw = ImageDraw.Draw(img)

        # LEFT ZONE: User name and Employee ID
        left_y = 40  # Starting Y position
        
        # Name in LEFT ZONE
        draw.text((self.left_zone_x, left_y), full_name, font=name_font, fill=text_color)
        
        # Employee ID in LEFT ZONE (below name)
        if hasattr(user, 'employee_id') and user.employee_id:
            left_y += 35
            draw.text((self.left_zone_x, left_y), f"Employee ID: {user.employee_id}", font=detail_font, fill=(102, 102, 102))
        
        # RIGHT ZONE: Digital signature text, designation, company
        right_y = 40  # Starting Y position
        
        # "Digitally signed by <Name>" in RIGHT ZONE
        draw.text((self.right_zone_x, right_y), f"Digitally signed by {full_name}", font=detail_font, fill=text_color)
        right_y += 25
        
        # Designation in RIGHT ZONE
        if user.designation:
            draw.text((self.right_zone_x, right_y), user.designation, font=detail_font, fill=(102, 102, 102))
            right_y += 25
        
        # Company name in RIGHT ZONE
        company_name = self._get_company_name(user)
        if company_name:
            draw.text((self.right_zone_x, right_y), company_name, font=detail_font, fill=(136, 136, 136))
            right_y += 25
        
        # Date placeholder in RIGHT ZONE
        draw.text((self.right_zone_x, right_y), "Date: [TO_BE_FILLED]", font=detail_font, fill=(51, 51, 51))

        # Convert back to RGB
        img = img.convert('RGB')

        # Save template to memory
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)

        # Create template data with versioned filename
        template_data = {
            'user_id': admin_detail.user.id,
            'full_name': full_name,
            'designation': user.designation or '',
            'employee_id': getattr(user, 'employee_id', '') or '',
            'company_name': self._get_company_name(user),
            'template_created_at': datetime.now().isoformat(),
            'template_version': '4.0',  # Updated version for center-aligned layout
            'template_type': 'admin'
        }

        # Create filename with versioned naming
        filename = f"admin_signature_template_v4_{admin_detail.user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        template_file = ContentFile(img_io.getvalue(), name=filename)

        return template_file, template_data

    def _get_company_logo(self, user):
        """
        Get company logo based on user type and hierarchy
        """
        # For EPC project admins, inherit from master's CompanyDetail
        if user.user_type == 'projectadmin' and user.admin_type == 'epc':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        return company_detail.company_logo
            except:
                pass
        
        # For other project admins, use their AdminDetail logo
        elif user.user_type == 'projectadmin':
            try:
                admin_detail = user.admin_detail
                if admin_detail and admin_detail.logo:
                    return admin_detail.logo
            except:
                pass

        # For EPCuser, inherit directly from master's CompanyDetail
        elif user.user_type == 'adminuser' and user.admin_type == 'epcuser':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        return company_detail.company_logo
            except:
                pass
        
        # For other admin users, get logo from their creator
        elif user.user_type == 'adminuser' and user.created_by:
            return self._get_company_logo(user.created_by)

        return None

    def _get_company_name(self, user):
        """
        Get company name based on user type and hierarchy
        """
        # For EPC project admins, inherit from master's CompanyDetail
        if user.user_type == 'projectadmin' and user.admin_type == 'epc':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_name:
                        return company_detail.company_name
            except:
                pass
        
        # For other project admins, use their company_name
        elif user.user_type == 'projectadmin':
            if user.company_name:
                return user.company_name

        # For EPCuser, inherit directly from master's CompanyDetail
        elif user.user_type == 'adminuser' and user.admin_type == 'epcuser':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_name:
                        return company_detail.company_name
            except:
                pass
        
        # For other admin users, get company name from their creator
        elif user.user_type == 'adminuser' and user.created_by:
            return self._get_company_name(user.created_by)

        return ""
    
    def generate_signed_document_signature(self, user_detail, sign_datetime=None):
        """
        Generate a signature for actual document signing with current date/time
        
        Args:
            user_detail: UserDetail instance
            sign_datetime: datetime object (defaults to now)
            
        Returns:
            ContentFile: Signature image with filled date/time
        """
        if not sign_datetime:
            sign_datetime = datetime.now()
            
        # Load the template
        if not user_detail.signature_template:
            raise ValueError("No signature template found for user")
            
        try:
            template_img = Image.open(user_detail.signature_template.path)
        except:
            raise ValueError("Could not load signature template")
        
        # Create a copy for modification
        signed_img = template_img.copy()
        draw = ImageDraw.Draw(signed_img)
        
        # Load font
        try:
            detail_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            detail_font = ImageFont.load_default()
        
        # Replace the date placeholder with actual timestamp
        date_text = f"Date: {sign_datetime.strftime('%Y.%m.%d %H:%M:%S %z')}"
        
        # Position in RIGHT ZONE (same as template generation)
        date_y = 40 + (25 * 3)  # Fourth line in right zone
        
        # Clear the placeholder area by drawing white rectangle
        placeholder_bbox = draw.textbbox((self.right_zone_x, date_y), "Date: [TO_BE_FILLED]", font=detail_font)
        draw.rectangle(placeholder_bbox, fill=(255, 255, 255))
        
        # Draw the actual date in RIGHT ZONE
        draw.text((self.right_zone_x, date_y), date_text, font=detail_font, fill=(51, 51, 51))
        
        # Save to memory
        img_io = io.BytesIO()
        signed_img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        # Create filename with timestamp
        filename = f"signature_{user_detail.user.id}_{sign_datetime.strftime('%Y%m%d_%H%M%S')}.png"
        return ContentFile(img_io.getvalue(), name=filename)


def create_user_signature_template(user_detail, logo_opacity=0.5):
    """
    Convenience function to create signature template for a user
    
    Args:
        user_detail: UserDetail instance
        logo_opacity: Float between 0.0 and 1.0 for logo transparency (default: 0.5)
    """
    generator = SignatureTemplateGenerator(logo_opacity=logo_opacity)

    template_file, template_data = generator.create_signature_template(user_detail)

    # Save to user detail
    user_detail.signature_template.save(template_file.name, template_file, save=False)
    user_detail.signature_template_data = template_data
    user_detail.save()

    return user_detail


def create_admin_signature_template(admin_detail, logo_opacity=0.5):
    """
    Convenience function to create signature template for an admin
    
    Args:
        admin_detail: AdminDetail instance
        logo_opacity: Float between 0.0 and 1.0 for logo transparency (default: 0.5)
    """
    generator = SignatureTemplateGenerator(logo_opacity=logo_opacity)

    template_file, template_data = generator.create_admin_signature_template(admin_detail)

    # Save to admin detail
    admin_detail.signature_template.save(template_file.name, template_file, save=False)
    admin_detail.signature_template_data = template_data
    admin_detail.save()

    return admin_detail


def generate_document_signature(user_detail, sign_datetime=None):
    """
    Generate signature for document signing
    """
    generator = SignatureTemplateGenerator()
    return generator.generate_signed_document_signature(user_detail, sign_datetime)