from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_plane', '0003_saasauditlog_saassubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaaSPlatformSettings',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False, serialize=False)),
                ('platform_name', models.CharField(default='Athens', max_length=200)),
                ('platform_url', models.URLField(blank=True)),
                ('support_email', models.EmailField(blank=True, max_length=254)),
                ('support_phone', models.CharField(blank=True, max_length=50)),
                ('logo_url', models.URLField(blank=True)),
                ('primary_color', models.CharField(blank=True, max_length=20)),
                ('email_from_name', models.CharField(blank=True, max_length=100)),
                ('email_from_address', models.EmailField(blank=True, max_length=254)),
                ('email_reply_to', models.EmailField(blank=True, max_length=254)),
                ('billing_provider', models.CharField(blank=True, max_length=100)),
                ('billing_mode', models.CharField(blank=True, max_length=50)),
                ('invoice_footer', models.TextField(blank=True)),
                ('session_timeout_minutes', models.PositiveIntegerField(default=60)),
                ('audit_retention_days', models.PositiveIntegerField(default=365)),
                ('allow_self_signup', models.BooleanField(default=False)),
                ('require_mfa', models.BooleanField(default=False)),
                ('maintenance_mode', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
