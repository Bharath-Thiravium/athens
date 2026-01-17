from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_backfill_project_tenant_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectMenuAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_menu_access_created', to='authentication.customuser')),
                ('module', models.ForeignKey(db_column='menu_module_id', on_delete=django.db.models.deletion.CASCADE, to='authentication.menumodule')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.project')),
            ],
            options={
                'unique_together': {('project', 'module')},
            },
        ),
    ]
