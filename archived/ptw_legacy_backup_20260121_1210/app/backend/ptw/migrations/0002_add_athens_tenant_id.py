"""
Migration to add athens_tenant_id to PTW models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ptw', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to all PTW models
        migrations.AddField(
            model_name='permittype',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permit',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='workflowtemplate',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='workflowinstance',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permitextension',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permitworker',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='hazardlibrary',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permithazard',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='gasreading',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permitphoto',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='digitalsignature',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permitaudit',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='permitapproval',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='escalationrule',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='notificationtemplate',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='systemintegration',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='compliancereport',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for key models
        migrations.AddIndex(
            model_name='permit',
            index=models.Index(fields=['athens_tenant_id'], name='ptw_permit_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='permit',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='ptw_permit_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='permittype',
            index=models.Index(fields=['athens_tenant_id'], name='ptw_permittype_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowinstance',
            index=models.Index(fields=['athens_tenant_id'], name='ptw_workflow_tenant_idx'),
        ),
    ]