"""
Migration to add athens_tenant_id to MOM models
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mom', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add athens_tenant_id to Mom model
        migrations.AddField(
            model_name='mom',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add athens_tenant_id to ParticipantResponse model
        migrations.AddField(
            model_name='participantresponse',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add athens_tenant_id to ParticipantAttendance model
        migrations.AddField(
            model_name='participantattendance',
            name='athens_tenant_id',
            field=models.UUIDField(null=True, help_text='Athens tenant identifier for multi-tenant isolation'),
        ),
        
        # Add indexes for athens_tenant_id
        migrations.AddIndex(
            model_name='mom',
            index=models.Index(fields=['athens_tenant_id'], name='mom_mom_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='mom',
            index=models.Index(fields=['athens_tenant_id', 'status'], name='mom_mom_tenant_status_idx'),
        ),
        migrations.AddIndex(
            model_name='participantresponse',
            index=models.Index(fields=['athens_tenant_id'], name='mom_response_tenant_idx'),
        ),
        migrations.AddIndex(
            model_name='participantattendance',
            index=models.Index(fields=['athens_tenant_id'], name='mom_attendance_tenant_idx'),
        ),
    ]