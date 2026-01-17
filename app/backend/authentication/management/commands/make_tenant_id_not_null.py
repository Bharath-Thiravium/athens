"""
Script to make athens_tenant_id NOT NULL across all Athens models.

This script should be run after populating existing data with tenant IDs.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps


class Command(BaseCommand):
    help = 'Make athens_tenant_id NOT NULL across all Athens models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get all models that should have athens_tenant_id
        models_to_update = [
            # Authentication models
            ('authentication', 'Project'),
            ('authentication', 'CustomUser'),
            ('authentication', 'UserDetail'),
            ('authentication', 'CompanyDetail'),
            ('authentication', 'AdminDetail'),
            
            # Worker models
            ('worker', 'Worker'),
            
            # Training models
            ('tbt', 'ToolboxTalk'),
            ('tbt', 'ToolboxTalkAttendance'),
            ('inductiontraining', 'InductionTraining'),
            ('inductiontraining', 'InductionAttendance'),
            
            # Safety models
            ('safetyobservation', 'SafetyObservation'),
            ('safetyobservation', 'SafetyObservationFile'),
            
            # Incident models
            ('incidentmanagement', 'Incident'),
            ('incidentmanagement', 'IncidentAttachment'),
            ('incidentmanagement', 'IncidentAuditLog'),
            ('incidentmanagement', 'IncidentNotification'),
            ('incidentmanagement', 'EightDProcess'),
            ('incidentmanagement', 'EightDDiscipline'),
            ('incidentmanagement', 'EightDTeam'),
            ('incidentmanagement', 'EightDContainmentAction'),
            ('incidentmanagement', 'EightDRootCause'),
            ('incidentmanagement', 'EightDCorrectiveAction'),
            ('incidentmanagement', 'EightDAnalysisMethod'),
            ('incidentmanagement', 'EightDPreventionAction'),
            
            # PTW models
            ('ptw', 'PermitType'),
            ('ptw', 'Permit'),
            ('ptw', 'WorkflowTemplate'),
            ('ptw', 'WorkflowInstance'),
            ('ptw', 'WorkflowStep'),
            ('ptw', 'PermitExtension'),
            ('ptw', 'PermitWorker'),
            ('ptw', 'HazardLibrary'),
            ('ptw', 'PermitHazard'),
            ('ptw', 'GasReading'),
            ('ptw', 'PermitPhoto'),
            ('ptw', 'DigitalSignature'),
            ('ptw', 'PermitAudit'),
            ('ptw', 'PermitApproval'),
            
            # MOM models
            ('mom', 'Mom'),
            ('mom', 'ParticipantResponse'),
            ('mom', 'ParticipantAttendance'),
            
            # Manpower models
            ('manpower', 'WorkType'),
            ('manpower', 'ManpowerEntry'),
            ('manpower', 'DailyManpowerSummary'),
            
            # Environment models
            ('environment', 'EnvironmentAspect'),
            ('environment', 'GenerationData'),
            ('environment', 'EmissionFactor'),
            ('environment', 'GHGActivity'),
            ('environment', 'WasteManifest'),
            ('environment', 'BiodiversityEvent'),
            ('environment', 'ESGPolicy'),
            ('environment', 'Grievance'),
            ('environment', 'EnvironmentalMonitoring'),
            ('environment', 'CarbonFootprint'),
            ('environment', 'WaterManagement'),
            ('environment', 'EnergyManagement'),
            ('environment', 'EnvironmentalIncident'),
            ('environment', 'SustainabilityTarget'),
            
            # Quality models
            ('quality', 'QualityStandard'),
            ('quality', 'QualityTemplate'),
            ('quality', 'QualityInspection'),
            ('quality', 'QualityDefect'),
            ('quality', 'SupplierQuality'),
            ('quality', 'QualityMetrics'),
            ('quality', 'QualityAlert'),
            
            # Inspection models
            ('inspection', 'Inspection'),
            ('inspection', 'InspectionItem'),
            ('inspection', 'InspectionReport'),
        ]
        
        total_updated = 0
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for app_label, model_name in models_to_update:
                        try:
                            # Get the model
                            model = apps.get_model(app_label, model_name)
                            table_name = model._meta.db_table
                            
                            # Check if athens_tenant_id column exists
                            cursor.execute(f"""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = '{table_name}' 
                                AND column_name = 'athens_tenant_id'
                            """)
                            
                            if not cursor.fetchone():
                                self.stdout.write(
                                    self.style.WARNING(f'Skipping {table_name} - athens_tenant_id column not found')
                                )
                                continue
                            
                            # Check for NULL values
                            cursor.execute(f"""
                                SELECT COUNT(*) 
                                FROM {table_name} 
                                WHERE athens_tenant_id IS NULL
                            """)
                            null_count = cursor.fetchone()[0]
                            
                            if null_count > 0:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f'ERROR: {table_name} has {null_count} records with NULL athens_tenant_id. '
                                        f'Run populate_tenant_ids first.'
                                    )
                                )
                                continue
                            
                            # Make column NOT NULL with proper constraint
                            if not dry_run:
                                # First ensure no NULL values exist
                                cursor.execute(f"""
                                    SELECT COUNT(*) FROM {table_name} 
                                    WHERE athens_tenant_id IS NULL
                                """)
                                null_count = cursor.fetchone()[0]
                                
                                if null_count > 0:
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f'BLOCKED: {table_name} has {null_count} NULL values. '
                                            f'Run populate_tenant_ids first.'
                                        )
                                    )
                                    continue
                                
                                # Add NOT NULL constraint
                                cursor.execute(f"""
                                    ALTER TABLE {table_name} 
                                    ALTER COLUMN athens_tenant_id SET NOT NULL
                                """)
                                
                                # Add foreign key constraint to athens_tenant
                                constraint_name = f"{table_name}_tenant_fk"
                                cursor.execute(f"""
                                    ALTER TABLE {table_name} 
                                    ADD CONSTRAINT {constraint_name} 
                                    FOREIGN KEY (athens_tenant_id) 
                                    REFERENCES athens_tenant(id) 
                                    ON DELETE RESTRICT
                                """)
                                
                                # Add performance index
                                index_name = f"{table_name}_athens_tenant_id_idx"
                                cursor.execute(f"""
                                    CREATE INDEX IF NOT EXISTS {index_name} 
                                    ON {table_name} (athens_tenant_id)
                                """)
                                
                                self.stdout.write(
                                    self.style.SUCCESS(f'✓ Updated {table_name} - athens_tenant_id is now NOT NULL')
                                )
                                total_updated += 1
                            else:
                                self.stdout.write(f'Would update {table_name} - athens_tenant_id to NOT NULL')
                        
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error updating {app_label}.{model_name}: {e}')
                            )
                
                if not dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ Successfully updated {total_updated} tables\n'
                            f'All athens_tenant_id columns are now NOT NULL with indexes'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            '\nDry run completed. Use --dry-run=false to apply changes.'
                        )
                    )
                
                # Rollback transaction if dry run
                if dry_run:
                    transaction.set_rollback(True)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Operation failed: {e}')
            )
            raise