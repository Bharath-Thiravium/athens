# Generated migration for PR7 - Permit Closeout Checklist

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ptw', '0004_add_workflow_statuses'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloseoutChecklistTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('risk_level', models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('extreme', 'Extreme')], max_length=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('items', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('permit_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closeout_templates', to='ptw.permittype')),
            ],
            options={
                'ordering': ['permit_type', 'risk_level', 'name'],
            },
        ),
        migrations.CreateModel(
            name='PermitCloseout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checklist', models.JSONField(default=dict)),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='closeouts_completed', to=settings.AUTH_USER_MODEL)),
                ('permit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='closeout', to='ptw.permit')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ptw.closeoutchecklisttemplate')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
