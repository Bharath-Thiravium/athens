# Generated migration for webhook models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ptw', '0009_add_version_and_idempotency'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookEndpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(max_length=500)),
                ('secret', models.CharField(help_text='HMAC secret for signature', max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('events', models.JSONField(default=list, help_text='List of event types to trigger')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_sent_at', models.DateTimeField(blank=True, null=True)),
                ('last_status_code', models.IntegerField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='webhooks_created', to='authentication.customuser')),
                ('project', models.ForeignKey(blank=True, help_text='Project scope (null = global)', null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.project')),
            ],
            options={
                'db_table': 'ptw_webhook_endpoint',
            },
        ),
        migrations.CreateModel(
            name='WebhookDeliveryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=100)),
                ('permit_id', models.IntegerField(blank=True, null=True)),
                ('dedupe_key', models.CharField(help_text='event+permit_id+hour for idempotency', max_length=255, unique=True)),
                ('payload', models.JSONField()),
                ('response_code', models.IntegerField(blank=True, null=True)),
                ('response_body', models.TextField(blank=True)),
                ('error', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='ptw.webhookendpoint')),
            ],
            options={
                'db_table': 'ptw_webhook_delivery_log',
            },
        ),
        migrations.AddIndex(
            model_name='webhookendpoint',
            index=models.Index(fields=['project', 'enabled'], name='ptw_webhook_project_enabled_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookendpoint',
            index=models.Index(fields=['enabled'], name='ptw_webhook_enabled_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['webhook', 'event'], name='ptw_webhook_delivery_webhook_event_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['permit_id'], name='ptw_webhook_delivery_permit_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['sent_at'], name='ptw_webhook_delivery_sent_idx'),
        ),
    ]
