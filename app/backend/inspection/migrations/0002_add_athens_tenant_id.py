"""
Migration to add athens_tenant_id to inspection models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to all inspection models
        migrations.AddField(
            model_name='inspection',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='inspectionitem',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='inspectionreport',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for athens_tenant_id
        migrations.AddIndex(
            model_name='inspection',
            index=models.Index(fields=['athens_tenant_id'], name='inspection_inspection_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='inspection',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='inspection_inspection_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='inspectionitem',
            index=models.Index(fields=['athens_tenant_id'], name='inspection_item_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='inspectionreport',
            index=models.Index(fields=['athens_tenant_id'], name='inspection_report_tenant_idx'),
        ),
    ]