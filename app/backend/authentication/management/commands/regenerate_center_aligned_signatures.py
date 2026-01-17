"""
Management command to regenerate all signature templates with center-aligned layout
"""

from django.core.management.base import BaseCommand
from authentication.models import UserDetail, AdminDetail
from authentication.signature_template_generator_new import create_user_signature_template, create_admin_signature_template
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Regenerate all signature templates with center-aligned layout (v4.0)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if template already exists',
        )

    def handle(self, *args, **options):
        force_regenerate = options['force']
        
        self.stdout.write(self.style.SUCCESS('Starting signature template regeneration with center-aligned layout...'))
        
        # Regenerate user signature templates
        user_count = 0
        user_success = 0
        user_errors = 0
        
        for user_detail in UserDetail.objects.select_related('user').all():
            user_count += 1
            user = user_detail.user
            
            # Skip if template exists and not forcing
            if user_detail.signature_template and not force_regenerate:
                # Check if it's already v4
                template_data = getattr(user_detail, 'signature_template_data', {})
                if template_data.get('template_version') == '4.0':
                    self.stdout.write(f'Skipping {user.username} - already has v4.0 template')
                    user_success += 1
                    continue
            
            # Check required fields
            if not user.name or not user.designation:
                self.stdout.write(
                    self.style.WARNING(f'Skipping {user.username} - missing required fields (name: {bool(user.name)}, designation: {bool(user.designation)})')
                )
                user_errors += 1
                continue
            
            try:
                # Delete old template if exists
                if user_detail.signature_template:
                    try:
                        user_detail.signature_template.delete(save=False)
                    except:
                        pass
                
                # Generate new center-aligned template
                create_user_signature_template(user_detail)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Generated center-aligned template for user: {user.username}')
                )
                user_success += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to generate template for {user.username}: {e}')
                )
                user_errors += 1
        
        # Regenerate admin signature templates
        admin_count = 0
        admin_success = 0
        admin_errors = 0
        
        for admin_detail in AdminDetail.objects.select_related('user').all():
            admin_count += 1
            user = admin_detail.user
            
            # Skip if template exists and not forcing
            if admin_detail.signature_template and not force_regenerate:
                # Check if it's already v4
                template_data = getattr(admin_detail, 'signature_template_data', {})
                if template_data.get('template_version') == '4.0':
                    self.stdout.write(f'Skipping admin {user.username} - already has v4.0 template')
                    admin_success += 1
                    continue
            
            # Check required fields
            if not user.name:
                self.stdout.write(
                    self.style.WARNING(f'Skipping admin {user.username} - missing name')
                )
                admin_errors += 1
                continue
            
            try:
                # Delete old template if exists
                if admin_detail.signature_template:
                    try:
                        admin_detail.signature_template.delete(save=False)
                    except:
                        pass
                
                # Generate new center-aligned template
                create_admin_signature_template(admin_detail)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Generated center-aligned template for admin: {user.username}')
                )
                admin_success += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to generate template for admin {user.username}: {e}')
                )
                admin_errors += 1\n        \n        # Summary\n        self.stdout.write('\\n' + '='*60)\n        self.stdout.write(self.style.SUCCESS('SIGNATURE TEMPLATE REGENERATION COMPLETE'))\n        self.stdout.write('='*60)\n        self.stdout.write(f'Users processed: {user_count}')\n        self.stdout.write(self.style.SUCCESS(f'User templates generated: {user_success}'))\n        if user_errors > 0:\n            self.stdout.write(self.style.ERROR(f'User template errors: {user_errors}'))\n        \n        self.stdout.write(f'\\nAdmins processed: {admin_count}')\n        self.stdout.write(self.style.SUCCESS(f'Admin templates generated: {admin_success}'))\n        if admin_errors > 0:\n            self.stdout.write(self.style.ERROR(f'Admin template errors: {admin_errors}'))\n        \n        total_success = user_success + admin_success\n        total_errors = user_errors + admin_errors\n        \n        self.stdout.write(f'\\nTOTAL SUCCESS: {total_success}')\n        if total_errors > 0:\n            self.stdout.write(self.style.ERROR(f'TOTAL ERRORS: {total_errors}'))\n        \n        self.stdout.write('\\nAll signature templates now use:')\n        self.stdout.write('- Fixed 800x200 canvas size')\n        self.stdout.write('- LEFT zone (x=20): User name + Employee ID')\n        self.stdout.write('- CENTER zone (horizontally centered): Company logo (50% opacity)')\n        self.stdout.write('- RIGHT zone (x=450): Digital signature text + designation + company')\n        self.stdout.write('- Version 4.0 with center-aligned layout')