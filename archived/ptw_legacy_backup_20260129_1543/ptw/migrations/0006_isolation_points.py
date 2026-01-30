# Generated migration for PR8 - Isolation Points Management

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ptw', '0005_closeout_checklist'),
    ]

    operations = [
        # Add structured isolation flags to PermitType
        migrations.AddField(
            model_name='permittype',
            name='requires_structured_isolation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permittype',
            name='requires_deisolation_on_closeout',
            field=models.BooleanField(default=False),
        ),
        
        # Create IsolationPointLibrary model
        migrations.CreateModel(
            name='IsolationPointLibrary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.CharField(blank=True, max_length=100)),
                ('asset_tag', models.CharField(blank=True, max_length=100)),
                ('point_code', models.CharField(max_length=50)),
                ('point_type', models.CharField(choices=[('valve', 'Valve'), ('breaker', 'Circuit Breaker'), ('switch', 'Switch'), ('disconnect', 'Disconnect'), ('line_blind', 'Line Blind'), ('fuse_pull', 'Fuse Pull'), ('other', 'Other')], max_length=20)),
                ('energy_type', models.CharField(choices=[('electrical', 'Electrical'), ('mechanical', 'Mechanical'), ('hydraulic', 'Hydraulic'), ('pneumatic', 'Pneumatic'), ('chemical', 'Chemical'), ('thermal', 'Thermal'), ('gravity', 'Gravity'), ('radiation', 'Radiation'), ('other', 'Other')], max_length=20)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('isolation_method', models.TextField(blank=True)),
                ('verification_method', models.TextField(blank=True)),
                ('requires_lock', models.BooleanField(default=True)),
                ('default_lock_count', models.PositiveIntegerField(default=1)),
                ('ppe_required', models.JSONField(blank=True, default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='isolation_points', to='authentication.project')),
            ],
            options={
                'ordering': ['point_code'],
            },
        ),
        
        # Create PermitIsolationPoint model
        migrations.CreateModel(
            name='PermitIsolationPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_point_name', models.CharField(blank=True, max_length=200)),
                ('custom_point_details', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('isolated', 'Isolated'), ('verified', 'Verified'), ('deisolated', 'De-isolated'), ('cancelled', 'Cancelled')], default='assigned', max_length=20)),
                ('required', models.BooleanField(default=True)),
                ('lock_applied', models.BooleanField(default=False)),
                ('lock_count', models.PositiveIntegerField(default=0)),
                ('lock_ids', models.JSONField(blank=True, default=list)),
                ('isolated_at', models.DateTimeField(blank=True, null=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('verification_notes', models.TextField(blank=True)),
                ('deisolated_at', models.DateTimeField(blank=True, null=True)),
                ('deisolated_notes', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deisolated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deisolations_performed', to=settings.AUTH_USER_MODEL)),
                ('isolated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='isolations_performed', to=settings.AUTH_USER_MODEL)),
                ('permit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='isolation_points', to='ptw.permit')),
                ('point', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='permit_assignments', to='ptw.isolationpointlibrary')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='isolations_verified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order', 'created_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='isolationpointlibrary',
            index=models.Index(fields=['project', 'point_code'], name='ptw_isolati_project_idx'),
        ),
        migrations.AddIndex(
            model_name='isolationpointlibrary',
            index=models.Index(fields=['project', 'asset_tag'], name='ptw_isolati_project_asset_idx'),
        ),
        migrations.AddIndex(
            model_name='isolationpointlibrary',
            index=models.Index(fields=['project', 'site'], name='ptw_isolati_project_site_idx'),
        ),
        migrations.AddIndex(
            model_name='permitisolationpoint',
            index=models.Index(fields=['permit', 'status'], name='ptw_permiti_permit_status_idx'),
        ),
        migrations.AddIndex(
            model_name='permitisolationpoint',
            index=models.Index(fields=['point'], name='ptw_permiti_point_idx'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='isolationpointlibrary',
            unique_together={('project', 'point_code')},
        ),
    ]
