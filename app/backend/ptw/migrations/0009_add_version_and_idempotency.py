# Generated migration for PR12 - Offline Sync Conflict Resolution

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ptw', '0006_isolation_points'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='permit',
            name='version',
            field=models.IntegerField(default=1, db_index=True),
        ),
        migrations.AddField(
            model_name='permitisolationpoint',
            name='version',
            field=models.IntegerField(default=1, db_index=True),
        ),
        migrations.AddField(
            model_name='permitcloseout',
            name='version',
            field=models.IntegerField(default=1, db_index=True),
        ),
        migrations.CreateModel(
            name='AppliedOfflineChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=255)),
                ('offline_id', models.CharField(max_length=255)),
                ('entity', models.CharField(max_length=50)),
                ('server_id', models.IntegerField(null=True, blank=True)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ptw_applied_offline_change',
                'indexes': [
                    models.Index(fields=['device_id', 'offline_id', 'entity'], name='ptw_applied_device_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='appliedofflinechange',
            constraint=models.UniqueConstraint(
                fields=['device_id', 'offline_id', 'entity'],
                name='unique_offline_change'
            ),
        ),
    ]
