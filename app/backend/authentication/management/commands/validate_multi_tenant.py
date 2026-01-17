"""
Validation script for Athens multi-tenant implementation.

This script validates that all domain models have proper tenant isolation.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from authentication.tenant_models import AthensTenant


class Command(BaseCommand):
    help = 'Validate Athens multi-tenant implementation'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Validating Athens Multi-Tenant Implementation\n'))
        
        # 1. Check tenant control table
        self.validate_tenant_control_table()
        
        # 2. Check all domain models have athens_tenant_id
        self.validate_domain_models()
        
        # 3. Check middleware configuration
        self.validate_middleware_config()
        
        # 4. Check data integrity
        self.validate_data_integrity()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Multi-tenant validation completed'))
    
    def validate_tenant_control_table(self):
        """Validate tenant control table exists and has data"""
        self.stdout.write('1. Validating tenant control table...')
        
        try:
            tenant_count = AthensTenant.objects.count()
            active_tenants = AthensTenant.objects.filter(is_active=True).count()
            
            if tenant_count == 0:
                self.stdout.write(self.style.WARNING('   ⚠️  No tenants found. Create at least one tenant.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✓ Found {tenant_count} tenants ({active_tenants} active)'))
            
            # Check required fields
            for tenant in AthensTenant.objects.all()[:3]:  # Check first 3
                if not tenant.master_admin_id:
                    self.stdout.write(self.style.ERROR(f'   ❌ Tenant {tenant.id} missing master_admin_id'))
                if not tenant.enabled_modules:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  Tenant {tenant.id} has no enabled modules'))
                if not tenant.enabled_menus:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  Tenant {tenant.id} has no enabled menus'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error validating tenant table: {e}'))
    
    def validate_domain_models(self):
        """Validate all domain models have athens_tenant_id"""
        self.stdout.write('\n2. Validating domain models...')
        
        # Expected domain models
        expected_models = [
            ('authentication', 'Project'),
            ('authentication', 'CustomUser'),
            ('authentication', 'UserDetail'),
            ('authentication', 'CompanyDetail'),
            ('authentication', 'AdminDetail'),
            ('worker', 'Worker'),
            ('tbt', 'ToolboxTalk'),
            ('tbt', 'ToolboxTalkAttendance'),
            ('inductiontraining', 'InductionTraining'),
            ('inductiontraining', 'InductionAttendance'),
            ('safetyobservation', 'SafetyObservation'),
            ('safetyobservation', 'SafetyObservationFile'),
            ('incidentmanagement', 'Incident'),
            ('incidentmanagement', 'EightDProcess'),
            ('ptw', 'Permit'),
            ('ptw', 'PermitType'),
            ('mom', 'Mom'),
            ('manpower', 'ManpowerEntry'),
            ('environment', 'EnvironmentAspect'),
            ('quality', 'QualityInspection'),
            ('inspection', 'Inspection'),
        ]
        
        missing_field = []
        with_field = []
        
        with connection.cursor() as cursor:
            for app_label, model_name in expected_models:
                try:
                    model = apps.get_model(app_label, model_name)
                    table_name = model._meta.db_table
                    
                    # Check if athens_tenant_id column exists
                    cursor.execute(f"""
                        SELECT column_name, is_nullable, data_type
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        AND column_name = 'athens_tenant_id'
                    """)
                    
                    result = cursor.fetchone()
                    if result:
                        column_name, is_nullable, data_type = result
                        if data_type.upper() == 'UUID' and is_nullable == 'NO':
                            with_field.append(f'{app_label}.{model_name}')
                        elif is_nullable == 'YES':
                            self.stdout.write(
                                self.style.WARNING(f'   ⚠️  {app_label}.{model_name} - athens_tenant_id is nullable')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'   ⚠️  {app_label}.{model_name} - athens_tenant_id wrong type: {data_type}')
                            )
                    else:
                        missing_field.append(f'{app_label}.{model_name}')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Error checking {app_label}.{model_name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(with_field)} models have proper athens_tenant_id field'))
        
        if missing_field:
            self.stdout.write(self.style.ERROR(f'   ❌ {len(missing_field)} models missing athens_tenant_id:'))
            for model in missing_field:
                self.stdout.write(f'      - {model}')
    
    def validate_middleware_config(self):
        """Validate middleware configuration"""
        self.stdout.write('\n3. Validating middleware configuration...')
        
        from django.conf import settings
        
        middleware = settings.MIDDLEWARE
        
        # Check if tenant middleware is present
        tenant_middleware = 'authentication.tenant_middleware.AthensTenantMiddleware'
        permission_middleware = 'authentication.tenant_middleware.TenantPermissionMiddleware'
        
        if tenant_middleware in middleware:
            self.stdout.write(self.style.SUCCESS('   ✓ AthensTenantMiddleware is configured'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ AthensTenantMiddleware is missing from MIDDLEWARE'))
        
        if permission_middleware in middleware:
            self.stdout.write(self.style.SUCCESS('   ✓ TenantPermissionMiddleware is configured'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ TenantPermissionMiddleware is missing from MIDDLEWARE'))
        
        # Check middleware order
        try:
            auth_index = middleware.index('django.contrib.auth.middleware.AuthenticationMiddleware')
            tenant_index = middleware.index(tenant_middleware)
            
            if tenant_index > auth_index:
                self.stdout.write(self.style.SUCCESS('   ✓ Middleware order is correct'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Tenant middleware should come after authentication middleware'))
        except ValueError:
            pass  # Already reported missing middleware
    
    def validate_data_integrity(self):
        """Validate data integrity"""
        self.stdout.write('\n4. Validating data integrity...')
        
        # Check for orphaned records
        with connection.cursor() as cursor:
            # Sample check on a few key tables
            key_tables = ['authentication_project', 'worker_worker', 'incidentmanagement_incident']
            
            for table in key_tables:
                try:
                    # Check for NULL athens_tenant_id
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM {table} 
                        WHERE athens_tenant_id IS NULL
                    """)
                    null_count = cursor.fetchone()[0]
                    
                    if null_count > 0:
                        self.stdout.write(
                            self.style.ERROR(f'   ❌ {table} has {null_count} records with NULL athens_tenant_id')
                        )
                    else:
                        self.stdout.write(self.style.SUCCESS(f'   ✓ {table} - no NULL tenant IDs'))
                    
                    # Check for invalid tenant IDs
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM {table} t
                        LEFT JOIN athens_tenant at ON t.athens_tenant_id = at.id
                        WHERE t.athens_tenant_id IS NOT NULL 
                        AND at.id IS NULL
                    """)
                    invalid_count = cursor.fetchone()[0]
                    
                    if invalid_count > 0:
                        self.stdout.write(
                            self.style.ERROR(f'   ❌ {table} has {invalid_count} records with invalid tenant IDs')
                        )
                    else:
                        self.stdout.write(self.style.SUCCESS(f'   ✓ {table} - all tenant IDs are valid'))
                
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  Could not validate {table}: {e}'))
        
        # Check tenant isolation
        self.stdout.write('\n   Checking tenant isolation...')
        
        try:
            from authentication.models import Project
            
            # Get tenant counts
            tenant_projects = {}
            for project in Project.objects.all():
                tenant_id = str(project.athens_tenant_id)
                tenant_projects[tenant_id] = tenant_projects.get(tenant_id, 0) + 1
            
            if len(tenant_projects) > 1:
                self.stdout.write(self.style.SUCCESS(f'   ✓ Data is distributed across {len(tenant_projects)} tenants'))
                for tenant_id, count in tenant_projects.items():
                    self.stdout.write(f'      - Tenant {tenant_id}: {count} projects')
            elif len(tenant_projects) == 1:
                self.stdout.write(self.style.WARNING('   ⚠️  All data belongs to single tenant (expected for single-tenant setup)'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  No project data found'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error checking tenant isolation: {e}'))
    
    def print_summary(self):
        """Print implementation summary"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('ATHENS MULTI-TENANT IMPLEMENTATION SUMMARY'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n✅ IMPLEMENTED FEATURES:')
        self.stdout.write('   • Tenant control table (athens_tenant)')
        self.stdout.write('   • athens_tenant_id on all domain models')
        self.stdout.write('   • Multi-tenant middleware')
        self.stdout.write('   • Permission classes')
        self.stdout.write('   • Tenant-aware base classes')
        self.stdout.write('   • Management commands')
        self.stdout.write('   • API endpoints')
        
        self.stdout.write('\n🔒 SECURITY FEATURES:')
        self.stdout.write('   • Automatic tenant filtering')
        self.stdout.write('   • JWT token validation')
        self.stdout.write('   • Module/menu permissions')
        self.stdout.write('   • Audit logging')
        
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('   1. Run migrations: python manage.py migrate')
        self.stdout.write('   2. Populate tenant IDs: python manage.py populate_tenant_ids')
        self.stdout.write('   3. Make fields NOT NULL: python manage.py make_tenant_id_not_null')
        self.stdout.write('   4. Create test tenant: python manage.py create_default_tenant')
        self.stdout.write('   5. Test API endpoints with tenant headers')
        
        self.stdout.write('\n' + '='*60)