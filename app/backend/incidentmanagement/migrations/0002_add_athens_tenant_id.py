"""
Migration to add athens_tenant_id to incident management models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidentmanagement', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to all incident management models
        migrations.AddField(
            model_name='incident',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentattachment',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentauditlog',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentnotification',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentcategory',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='riskassessmenttemplate',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentmetrics',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentworkflow',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentcostcenter',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='incidentlearning',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # 8D Process models
        migrations.AddField(
            model_name='eightdprocess',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightddiscipline',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdteam',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdcontainmentaction',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdrootcause',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdcorrectiveaction',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdanalysismethod',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='eightdpreventionaction',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for athens_tenant_id on key models
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['athens_tenant_id'], name='incident_incident_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='incident_incident_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['athens_tenant_id', 'severity_level'], name='incident_incident_tenant_severity_idx'),
        ),
        migrations.AddIndex(
            model_name='eightdprocess',
            index=models.Index(fields=['athens_tenant_id'], name='incident_8d_process_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='eightdprocess',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='incident_8d_process_tenant_status_idx'),
        ),
    ]