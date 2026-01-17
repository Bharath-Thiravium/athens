from django.core.management.base import BaseCommand
from authentication.models import UserDetail, AdminDetail
from authentication.signature_template_generator import SignatureTemplateGenerator
import os


class Command(BaseCommand):
    help = 'Force regenerate signature templates bypassing all checks'

    def handle(self, *args, **options):
        self.stdout.write('Force regenerating signature templates...')
        
        generator = SignatureTemplateGenerator()
        
        # Force regenerate UserDetail templates
        user_details = UserDetail.objects.all()
        user_count = 0
        
        for user_detail in user_details:
            user = user_detail.user
            
            # Check if user has minimum required data
            if not user.name:
                self.stdout.write(f'⚠️ Skipping {user.username}: No name')
                continue
                
            try:
                # Force delete old template file
                if user_detail.signature_template:
                    try:
                        if os.path.exists(user_detail.signature_template.path):
                            os.remove(user_detail.signature_template.path)
                    except:
                        pass
                
                # Clear database fields
                user_detail.signature_template = None
                user_detail.signature_template_data = None
                user_detail.save()
                
                # Generate new template
                template_file, template_data = generator.create_signature_template(user_detail)
                user_detail.signature_template.save(template_file.name, template_file, save=False)
                user_detail.signature_template_data = template_data
                user_detail.save()
                
                user_count += 1
                self.stdout.write(f'✅ Force regenerated template for: {user.username}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed for {user.username}: {e}')
        
        # Force regenerate AdminDetail templates  
        admin_details = AdminDetail.objects.exclude(user__admin_type='master')
        admin_count = 0
        
        for admin_detail in admin_details:
            user = admin_detail.user
            
            if not user.name:
                self.stdout.write(f'⚠️ Skipping admin {user.username}: No name')
                continue
                
            try:
                # Force delete old template file
                if admin_detail.signature_template:
                    try:
                        if os.path.exists(admin_detail.signature_template.path):
                            os.remove(admin_detail.signature_template.path)
                    except:
                        pass
                
                # Clear database fields
                admin_detail.signature_template = None
                admin_detail.signature_template_data = None
                admin_detail.save()
                
                # Generate new template
                template_file, template_data = generator.create_admin_signature_template(admin_detail)
                admin_detail.signature_template.save(template_file.name, template_file, save=False)
                admin_detail.signature_template_data = template_data
                admin_detail.save()
                
                admin_count += 1
                self.stdout.write(f'✅ Force regenerated admin template for: {user.username}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed for admin {user.username}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Force regenerated {user_count} user templates and {admin_count} admin templates'
            )
        )