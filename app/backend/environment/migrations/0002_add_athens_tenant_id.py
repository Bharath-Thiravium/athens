"""
Migration to add athens_tenant_id to environment models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('environment', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to all environment models
        migrations.AddField(
            model_name='environmentaspect',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='generationdata',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='emissionfactor',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='ghgactivity',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='wastemanifest',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='biodiversityevent',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='esgpolicy',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='grievance',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='environmentalmonitoring',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='carbonfootprint',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='watermanagement',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='energymanagement',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='environmentalincident',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='sustainabilitytarget',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for key models
        migrations.AddIndex(
            model_name='environmentaspect',
            index=models.Index(fields=['athens_tenant_id'], name='env_aspect_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='generationdata',
            index=models.Index(fields=['athens_tenant_id'], name='env_generation_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='wastemanifest',
            index=models.Index(fields=['athens_tenant_id'], name='env_waste_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='environmentalincident',
            index=models.Index(fields=['athens_tenant_id'], name='env_incident_tenant_idx'),
        ),
    ]