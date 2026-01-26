from django.core.management.base import BaseCommand
from authentication.models import UserDetail, AdminDetail
from authentication.signature_template_generator_new import create_signature_template
import os

class Command(BaseCommand):
    help = 'Reset and regenerate signature template for a user'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='User ID to reset template for')
        parser.add_argument('--username', type=str, help='Username to reset template for')
        parser.add_argument('--all', action='store_true', help='Reset all templates')

    def handle(self, *args, **options):
        if options['all']:
            self.reset_all_templates()
        elif options['user_id']:
            self.reset_user_template(user_id=options['user_id'])
        elif options['username']:
            self.reset_user_template(username=options['username'])
        else:
            self.stdout.write('Please specify --user-id, --username, or --all')

    def reset_user_template(self, user_id=None, username=None):
        try:
            # Find UserDetail
            if user_id:
                detail = UserDetail.objects.select_related('user').get(user__id=user_id)
            else:
                detail = UserDetail.objects.select_related('user').get(user__username=username)
            
            self.reset_template(detail, 'UserDetail')
            
        except UserDetail.DoesNotExist:
            try:
                # Try AdminDetail
                if user_id:
                    detail = AdminDetail.objects.select_related('user').get(user__id=user_id)
                else:
                    detail = AdminDetail.objects.select_related('user').get(user__username=username)
                
                self.reset_template(detail, 'AdminDetail')
                
            except AdminDetail.DoesNotExist:
                self.stdout.write(f'User not found: {user_id or username}')

    def reset_template(self, detail, detail_type):
        user = detail.user
        self.stdout.write(f'Resetting template for {detail_type} user: {user.username} (ID: {user.id})')
        
        # Delete old template file
        if detail.signature_template:
            try:
                old_path = detail.signature_template.path
                if os.path.exists(old_path):
                    os.remove(old_path)
                    self.stdout.write(f'Deleted old template file: {old_path}')
                detail.signature_template.delete(save=False)
            except Exception as e:
                self.stdout.write(f'Error deleting old template: {e}')
        
        # Clear template fields
        detail.signature_template = None
        if hasattr(detail, 'signature_template_data'):
            detail.signature_template_data = None
        detail.save(update_fields=['signature_template'])
        
        # Regenerate template
        try:
            create_signature_template(detail)
            self.stdout.write(f'✅ Template reset and regenerated for user {user.username}')
        except Exception as e:
            self.stdout.write(f'❌ Error regenerating template: {e}')

    def reset_all_templates(self):
        self.stdout.write('Resetting all signature templates...')
        
        # Reset UserDetail templates
        for detail in UserDetail.objects.filter(signature_template__isnull=False):
            self.reset_template(detail, 'UserDetail')
        
        # Reset AdminDetail templates  
        for detail in AdminDetail.objects.filter(signature_template__isnull=False):
            self.reset_template(detail, 'AdminDetail')
        
        self.stdout.write('All templates reset complete!')