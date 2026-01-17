from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import os
import io
from datetime import datetime

class SignatureTemplateGenerator:
    def __init__(self):
        self.template_width = 405  # Reduced by 10% (450 * 0.9)
        self.template_height = 162  # Reduced by 10% (180 * 0.9)

    def create_signature_template(self, user_detail):
        img = Image.new('RGB', (self.template_width, self.template_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            detail_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            name_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
        
        text_color = (0, 0, 0)
        full_name = f"{user_detail.user.name or ''} {user_detail.user.surname or ''}".strip()
        if not full_name:
            full_name = user_detail.user.username
        
        # Add company logo
        company_logo = self._get_company_logo(user_detail.user)
        if company_logo and os.path.exists(company_logo.path):
            try:
                logo = Image.open(company_logo.path)
                content_width = self.template_width - 30
                content_height = self.template_height - 30
                scale_w = content_width / logo.width
                scale_h = content_height / logo.height
                scale = min(scale_w, scale_h, 1.0)
                new_width = int(logo.width * scale)
                new_height = int(logo.height * scale)
                logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logo_rgba = logo.convert('RGBA')
                alpha = logo_rgba.split()[-1]
                alpha = alpha.point(lambda p: int(p * 0.5))
                logo_rgba.putalpha(alpha)
                logo_x = (self.template_width - logo.width) // 2
                logo_y = (self.template_height - logo.height) // 2
                background = Image.new('RGBA', (self.template_width, self.template_height), (255, 255, 255, 255))
                background.paste(logo_rgba, (logo_x, logo_y), logo_rgba)
                img = Image.alpha_composite(img.convert('RGBA'), background).convert('RGB')
                draw = ImageDraw.Draw(img)
            except:
                pass
        
        # Layout with strict boundaries
        left_margin = 15
        left_max_width = 180  # Maximum width for left region
        right_margin = 215  # Start of right region with buffer
        right_max_width = 175  # Maximum width for right region
        left_y = 30
        line_height = 16
        
        # Left side - constrained to left region
        draw.text((left_margin, left_y), full_name[:25], font=name_font, fill=text_color)  # Truncate if too long
        left_y += 30
        
        designation = user_detail.user.designation or ""
        if designation:
            draw.text((left_margin, left_y), designation[:20], font=detail_font, fill=text_color)  # Truncate
            left_y += line_height
        
        department = user_detail.user.department or ""
        if department:
            draw.text((left_margin, left_y), department[:20], font=detail_font, fill=text_color)  # Truncate
        
        # Right side - constrained to right region
        right_y = 30
        draw.text((right_margin, right_y), "Digitally signed", font=detail_font, fill=text_color)
        right_y += line_height
        draw.text((right_margin, right_y), f"by {full_name[:15]}", font=detail_font, fill=text_color)  # Truncate
        right_y += line_height
        
        employee_id = user_detail.employee_id or ""
        if employee_id:
            draw.text((right_margin, right_y), f"ID: {employee_id[:10]}", font=detail_font, fill=text_color)  # Shorter label
            right_y += line_height
        
        company_name = self._get_company_name(user_detail.user)
        if company_name:
            draw.text((right_margin, right_y), company_name[:20], font=detail_font, fill=text_color)  # Truncate
        
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        template_data = {
            'user_id': user_detail.user.id,
            'full_name': full_name,
            'designation': user_detail.user.designation or '',
            'company_name': self._get_company_name(user_detail.user),
            'template_created_at': datetime.now().isoformat(),
            'template_version': '2.0'
        }
        
        filename = f"signature_template_{user_detail.user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        template_file = ContentFile(img_io.getvalue(), name=filename)
        
        return template_file, template_data

    def _get_company_logo(self, user):
        if user.user_type == 'adminuser' and user.admin_type == 'epcuser':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_logo:
                        return company_detail.company_logo
            except:
                pass
        return None

    def _get_company_name(self, user):
        if user.user_type == 'adminuser' and user.admin_type == 'epcuser':
            try:
                from .models import CustomUser
                master_admin = CustomUser.objects.filter(admin_type='master').first()
                if master_admin and hasattr(master_admin, 'company_detail'):
                    company_detail = master_admin.company_detail
                    if company_detail and company_detail.company_name:
                        return company_detail.company_name
            except:
                pass
        return ""

def create_user_signature_template(user_detail):
    generator = SignatureTemplateGenerator()
    template_file, template_data = generator.create_signature_template(user_detail)
    user_detail.signature_template.save(template_file.name, template_file, save=False)
    user_detail.signature_template_data = template_data
    user_detail.save()
    return user_detail
