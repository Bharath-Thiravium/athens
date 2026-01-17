"""
Migration to add athens_tenant_id to safety observation models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('safetyobservation', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to SafetyObservation model
        migrations.AddField(
            model_name='safetyobservation',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add athens_tenant_id to SafetyObservationFile model
        migrations.AddField(
            model_name='safetyobservationfile',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for athens_tenant_id
        migrations.AddIndex(
            model_name='safetyobservation',
            index=models.Index(fields=['athens_tenant_id'], name='safety_obs_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='safetyobservation',
            index=models.Index(fields=['athens_tenant_id', 'observationStatus'], name='safety_obs_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='safetyobservationfile',
            index=models.Index(fields=['athens_tenant_id'], name='safety_obs_file_tenant_idx'),
        ),
    ]