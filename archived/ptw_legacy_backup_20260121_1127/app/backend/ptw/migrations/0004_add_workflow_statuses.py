# Generated migration for adding workflow statuses

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ptw', '0003_remove_permit_ptw_permit_tenant_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('pending_verification', 'Pending Verification'),
                    ('under_review', 'Under Review'),
                    ('pending_approval', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('active', 'Active'),
                    ('suspended', 'Suspended'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                    ('expired', 'Expired'),
                    ('rejected', 'Rejected'),
                ],
                default='draft',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='workflowstep',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('completed', 'Completed'),
                    ('skipped', 'Skipped'),
                    ('obsolete', 'Obsolete'),
                ],
                default='pending',
                max_length=20
            ),
        ),
    ]
