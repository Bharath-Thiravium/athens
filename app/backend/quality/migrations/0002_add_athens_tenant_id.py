"""
Migration to add athens_tenant_id to quality models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to all quality models
        migrations.AddField(
            model_name='qualitystandard',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='qualitytemplate',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='qualityinspection',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='qualitydefect',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='supplierquality',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='qualitymetrics',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        migrations.AddField(
            model_name='qualityalert',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for key models
        migrations.AddIndex(
            model_name='qualitytemplate',
            index=models.Index(fields=['athens_tenant_id'], name='quality_template_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='qualityinspection',
            index=models.Index(fields=['athens_tenant_id'], name='quality_inspection_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='qualityinspection',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='quality_inspection_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='qualitydefect',
            index=models.Index(fields=['athens_tenant_id'], name='quality_defect_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='supplierquality',
            index=models.Index(fields=['athens_tenant_id'], name='quality_supplier_tenant_idx'),
        ),
    ]