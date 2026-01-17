"""
Django management command to create signature templates for existing users
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from authentication.models import UserDetail, AdminDetail, CustomUser
from authentication.signature_template_generator import create_user_signature_template, create_admin_signature_template


class Command(BaseCommand):
    help = 'Create signature templates for existing users who don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating templates',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate templates even if they already exist',
        )
        parser.add_argument(
            '--user-type',
            choices=['adminuser', 'projectadmin', 'all'],
            default='all',
            help='Create templates for specific user type only',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        user_type_filter = options['user_type']

        self.stdout.write(
            self.style.SUCCESS(
                f"🎨 Creating signature templates for existing users..."
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN MODE - No templates will be created")
            )

        # Counters
        userdetail_created = 0
        userdetail_skipped = 0
        admindetail_created = 0
        admindetail_skipped = 0
        errors = 0

        # Process UserDetail templates (for adminusers)
        if user_type_filter in ['adminuser', 'all']:
            self.stdout.write("\n📋 Processing UserDetail templates (adminusers)...")
            
            userdetails = UserDetail.objects.select_related('user').all()
            
            for user_detail in userdetails:
                user = user_detail.user
                
                # Check if user has required fields
                if not (user.name and user.surname and user.designation):
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Skipping {user.username}: Missing required fields (name: {bool(user.name)}, surname: {bool(user.surname)}, designation: {bool(user.designation)})"
                        )
                    )
                    userdetail_skipped += 1
                    continue
                
                # Check if template already exists
                if user_detail.signature_template and not force:
                    self.stdout.write(
                        f"ℹ️  Skipping {user.username}: Template already exists"
                    )
                    userdetail_skipped += 1
                    continue
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Would create UserDetail template for: {user.username} ({user.name} {user.surname}, {user.designation})"
                        )
                    )
                    userdetail_created += 1
                else:
                    try:
                        with transaction.atomic():
                            # Delete existing template if force is enabled
                            if force and user_detail.signature_template:
                                user_detail.signature_template.delete(save=False)
                                user_detail.signature_template_data = None
                            
                            # Create new template
                            create_user_signature_template(user_detail)
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✅ Created UserDetail template for: {user.username}"
                                )
                            )
                            userdetail_created += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Error creating UserDetail template for {user.username}: {e}"
                            )
                        )
                        errors += 1

        # Process AdminDetail templates (for projectadmins, except master)
        if user_type_filter in ['projectadmin', 'all']:
            self.stdout.write("\n📋 Processing AdminDetail templates (projectadmins)...")
            
            admindetails = AdminDetail.objects.select_related('user').all()
            
            for admin_detail in admindetails:
                user = admin_detail.user
                
                # Skip master admin
                if user.admin_type in ['master', 'masteradmin']:
                    self.stdout.write(
                        f"⚠️  Skipping master admin: {user.username}"
                    )
                    admindetail_skipped += 1
                    continue
                
                # Check if user has required fields (only name required for admin signatures)
                if not user.name:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Skipping {user.username}: Missing required field (name: {bool(user.name)})"
                        )
                    )
                    admindetail_skipped += 1
                    continue
                
                # Check if template already exists
                if admin_detail.signature_template and not force:
                    self.stdout.write(
                        f"ℹ️  Skipping {user.username}: Template already exists"
                    )
                    admindetail_skipped += 1
                    continue
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Would create AdminDetail template for: {user.username} ({user.name}, {user.admin_type})"
                        )
                    )
                    admindetail_created += 1
                else:
                    try:
                        with transaction.atomic():
                            # Delete existing template if force is enabled
                            if force and admin_detail.signature_template:
                                admin_detail.signature_template.delete(save=False)
                                admin_detail.signature_template_data = None
                            
                            # Create new template
                            create_admin_signature_template(admin_detail)
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✅ Created AdminDetail template for: {user.username}"
                                )
                            )
                            admindetail_created += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Error creating AdminDetail template for {user.username}: {e}"
                            )
                        )
                        errors += 1

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 SUMMARY"))
        self.stdout.write("="*60)
        
        if user_type_filter in ['adminuser', 'all']:
            self.stdout.write(f"👥 UserDetail Templates:")
            self.stdout.write(f"   ✅ Created: {userdetail_created}")
            self.stdout.write(f"   ⏭️  Skipped: {userdetail_skipped}")
        
        if user_type_filter in ['projectadmin', 'all']:
            self.stdout.write(f"👨‍💼 AdminDetail Templates:")
            self.stdout.write(f"   ✅ Created: {admindetail_created}")
            self.stdout.write(f"   ⏭️  Skipped: {admindetail_skipped}")
        
        total_created = userdetail_created + admindetail_created
        total_skipped = userdetail_skipped + admindetail_skipped
        
        self.stdout.write(f"🎯 Total Created: {total_created}")
        self.stdout.write(f"⏭️  Total Skipped: {total_skipped}")
        self.stdout.write(f"❌ Errors: {errors}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n🔍 This was a dry run. Run without --dry-run to actually create templates."
                )
            )
        elif total_created > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Successfully created {total_created} signature templates!"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 No new templates were created. All eligible users already have templates."
                )
            )
