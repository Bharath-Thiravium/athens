"""
Data migration script to populate athens_tenant_id for existing records.

This script should be run after the schema migrations to populate
the athens_tenant_id field for all existing records.
"""

import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from authentication.models import Project, CustomUser, UserDetail, CompanyDetail, AdminDetail
from authentication.tenant_models import AthensTenant, DEFAULT_MODULES, DEFAULT_MENUS
from worker.models import Worker
from incidentmanagement.models import Incident


class Command(BaseCommand):
    help = 'Populate athens_tenant_id for existing records'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Specific tenant ID to use for all records (UUID format)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
    
    def handle(self, *args, **options):
        tenant_id = options.get('tenant_id')
        dry_run = options.get('dry_run', False)
        
        if tenant_id:
            try:
                tenant_id = uuid.UUID(tenant_id)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid tenant ID format: {tenant_id}')
                )
                return
        else:
            # Create a default tenant for existing data
            tenant_id = uuid.uuid4()
        
        self.stdout.write(f'Using tenant ID: {tenant_id}')\n        \n        if dry_run:\n            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))\n        \n        try:\n            with transaction.atomic():\n                # Create or get the tenant\n                tenant, created = AthensTenant.objects.get_or_create(\n                    id=tenant_id,\n                    defaults={\n                        'master_admin_id': uuid.uuid4(),  # Placeholder\n                        'enabled_modules': DEFAULT_MODULES.copy(),\n                        'enabled_menus': DEFAULT_MENUS.copy(),\n                        'is_active': True,\n                        'tenant_name': 'Migrated Data Tenant',\n                    }\n                )\n                \n                if created:\n                    self.stdout.write(\n                        self.style.SUCCESS(f'Created new tenant: {tenant.tenant_name}')\n                    )\n                else:\n                    self.stdout.write(\n                        self.style.SUCCESS(f'Using existing tenant: {tenant.tenant_name}')\n                    )\n                \n                # Update models that need athens_tenant_id\n                models_to_update = [\n                    (Project, 'projects'),\n                    (CustomUser, 'users'),\n                    (UserDetail, 'user details'),\n                    (CompanyDetail, 'company details'),\n                    (AdminDetail, 'admin details'),\n                    (Worker, 'workers'),\n                    (Incident, 'incidents'),\n                ]\n                \n                total_updated = 0\n                \n                for model_class, model_name in models_to_update:\n                    # Find records without athens_tenant_id\n                    records_to_update = model_class.objects.filter(\n                        athens_tenant_id__isnull=True\n                    )\n                    \n                    count = records_to_update.count()\n                    \n                    if count > 0:\n                        self.stdout.write(\n                            f'Found {count} {model_name} without athens_tenant_id'\n                        )\n                        \n                        if not dry_run:\n                            # Update records\n                            updated = records_to_update.update(\n                                athens_tenant_id=tenant_id\n                            )\n                            \n                            self.stdout.write(\n                                self.style.SUCCESS(\n                                    f'Updated {updated} {model_name} with athens_tenant_id'\n                                )\n                            )\n                            total_updated += updated\n                        else:\n                            self.stdout.write(\n                                f'Would update {count} {model_name}'\n                            )\n                    else:\n                        self.stdout.write(\n                            f'No {model_name} need updating'\n                        )\n                \n                if not dry_run:\n                    self.stdout.write(\n                        self.style.SUCCESS(\n                            f'\\nMigration completed successfully!\\n'\n                            f'Total records updated: {total_updated}\\n'\n                            f'Tenant ID: {tenant_id}'\n                        )\n                    )\n                else:\n                    self.stdout.write(\n                        self.style.WARNING(\n                            '\\nDry run completed. Use --dry-run=false to apply changes.'\n                        )\n                    )\n                \n                # Rollback transaction if dry run\n                if dry_run:\n                    transaction.set_rollback(True)\n                \n        except Exception as e:\n            self.stdout.write(\n                self.style.ERROR(f'Migration failed: {e}')\n            )\n            raise