"""
Management command to create a default Athens tenant for testing/development.

This command creates a default tenant with all modules and menus enabled.
"""

import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from authentication.tenant_models import AthensTenant, DEFAULT_MODULES, DEFAULT_MENUS


class Command(BaseCommand):
    help = 'Create a default Athens tenant for testing/development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Specific tenant ID to use (UUID format)',
        )
        parser.add_argument(
            '--master-admin-id',
            type=str,
            help='Master admin ID (UUID format)',
        )
        parser.add_argument(
            '--tenant-name',
            type=str,
            default='Default Test Tenant',
            help='Tenant name',
        )
        parser.add_argument(
            '--company-id',
            type=str,
            help='Company ID (UUID format)',
        )
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Create tenant with minimal modules/menus',
        )
    
    def handle(self, *args, **options):
        # Generate or use provided IDs
        tenant_id = options.get('tenant_id')
        if tenant_id:
            try:
                tenant_id = uuid.UUID(tenant_id)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid tenant ID format: {tenant_id}')
                )
                return
        else:
            tenant_id = uuid.uuid4()
        
        master_admin_id = options.get('master_admin_id')
        if master_admin_id:
            try:
                master_admin_id = uuid.UUID(master_admin_id)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid master admin ID format: {master_admin_id}')
                )
                return
        else:
            master_admin_id = uuid.uuid4()
        
        company_id = options.get('company_id')
        if company_id:
            try:
                company_id = uuid.UUID(company_id)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid company ID format: {company_id}')
                )
                return
        
        tenant_name = options.get('tenant_name')
        minimal = options.get('minimal', False)
        
        # Check if tenant already exists
        if AthensTenant.objects.filter(id=tenant_id).exists():
            self.stdout.write(
                self.style.ERROR(f'Tenant with ID {tenant_id} already exists')
            )
            return
        
        # Determine modules and menus
        if minimal:
            enabled_modules = ['authentication', 'worker', 'safetyobservation']
            enabled_menus = ['dashboard', 'workers', 'safety']
        else:
            enabled_modules = DEFAULT_MODULES.copy()
            enabled_menus = DEFAULT_MENUS.copy()
        
        try:
            with transaction.atomic():
                # Create tenant
                tenant = AthensTenant.objects.create(
                    id=tenant_id,
                    company_id=company_id,
                    master_admin_id=master_admin_id,
                    enabled_modules=enabled_modules,
                    enabled_menus=enabled_menus,
                    is_active=True,
                    tenant_name=tenant_name,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created tenant:\n'
                        f'  ID: {tenant.id}\n'
                        f'  Name: {tenant.tenant_name}\n'
                        f'  Master Admin ID: {tenant.master_admin_id}\n'
                        f'  Company ID: {tenant.company_id}\n'
                        f'  Enabled Modules: {len(tenant.enabled_modules)}\n'
                        f'  Enabled Menus: {len(tenant.enabled_menus)}\n'
                        f'  Active: {tenant.is_active}'
                    )
                )
                
                # Display enabled modules and menus
                if not minimal:
                    self.stdout.write('\nEnabled Modules:')
                    for module in tenant.enabled_modules:
                        self.stdout.write(f'  - {module}')
                    
                    self.stdout.write('\nEnabled Menus:')
                    for menu in tenant.enabled_menus:
                        self.stdout.write(f'  - {menu}')
                
                # Provide usage instructions
                self.stdout.write(
                    self.style.WARNING(
                        f'\nTo use this tenant in API requests, include:\n'
                        f'  Header: X-Athens-Tenant-ID: {tenant.id}\n'
                        f'  Or JWT payload: "athens_tenant_id": "{tenant.id}"'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create tenant: {e}')
            )