from django.core.management.base import BaseCommand
from authentication.models import UserDetail, AdminDetail
from authentication.signature_template_generator import SignatureTemplateGenerator


class Command(BaseCommand):
    help = 'Regenerate all signature templates with new design'

    def handle(self, *args, **options):
        self.stdout.write('Regenerating signature templates...')
        
        # Regenerate UserDetail signature templates
        user_details = UserDetail.objects.filter(user__name__isnull=False).exclude(user__name='')
        user_count = 0
        
        for user_detail in user_details:
            try:
                # Delete old template
                if user_detail.signature_template:
                    user_detail.signature_template.delete(save=False)
                    user_detail.signature_template = None
                    user_detail.signature_template_data = None
                    user_detail.save()
                
                # Create new template directly without signal checks
                generator = SignatureTemplateGenerator()
                template_file, template_data = generator.create_signature_template(user_detail)
                user_detail.signature_template.save(template_file.name, template_file, save=False)
                user_detail.signature_template_data = template_data
                user_detail.save()
                user_count += 1
                self.stdout.write(f'✅ Regenerated template for user: {user_detail.user.username}')
            except Exception as e:
                self.stdout.write(f'❌ Failed to regenerate template for user {user_detail.user.username}: {e}')
        
        # Regenerate AdminDetail signature templates
        admin_details = AdminDetail.objects.filter(user__name__isnull=False).exclude(user__name='').exclude(user__admin_type='master')
        admin_count = 0
        
        for admin_detail in admin_details:
            try:
                # Delete old template
                if admin_detail.signature_template:
                    admin_detail.signature_template.delete(save=False)
                    admin_detail.signature_template = None
                    admin_detail.signature_template_data = None
                    admin_detail.save()
                
                # Create new template directly without signal checks
                generator = SignatureTemplateGenerator()
                template_file, template_data = generator.create_admin_signature_template(admin_detail)
                admin_detail.signature_template.save(template_file.name, template_file, save=False)
                admin_detail.signature_template_data = template_data
                admin_detail.save()
                admin_count += 1
                self.stdout.write(f'✅ Regenerated admin template for: {admin_detail.user.username}')
            except Exception as e:
                self.stdout.write(f'❌ Failed to regenerate admin template for {admin_detail.user.username}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully regenerated {user_count} user templates and {admin_count} admin templates'
            )
        )