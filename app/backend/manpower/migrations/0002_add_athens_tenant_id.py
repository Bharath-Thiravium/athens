"""
Migration to add athens_tenant_id to manpower models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manpower', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to WorkType model
        migrations.AddField(
            model_name='worktype',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add athens_tenant_id to ManpowerEntry model
        migrations.AddField(
            model_name='manpowerentry',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add athens_tenant_id to DailyManpowerSummary model
        migrations.AddField(
            model_name='dailymanpowersummary',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for athens_tenant_id
        migrations.AddIndex(
            model_name='worktype',
            index=models.Index(fields=['athens_tenant_id'], name='manpower_worktype_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='manpowerentry',
            index=models.Index(fields=['athens_tenant_id'], name='manpower_entry_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='manpowerentry',
            index=models.Index(fields=['athens_tenant_id', 'date'], name='manpower_entry_tenant_date_idx'),
        ),
        migrations.AddIndex(
            model_name='dailymanpowersummary',
            index=models.Index(fields=['athens_tenant_id'], name='manpower_summary_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='dailymanpowersummary',
            index=models.Index(fields=['athens_tenant_id', 'date'], name='manpower_summary_tenant_date_idx'),
        ),
    ]