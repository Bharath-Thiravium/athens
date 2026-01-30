# Generated migration for password reset control fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_project_menu_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='can_reset_password',
            field=models.BooleanField(default=True, help_text='Whether user can reset their password'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='password_set_by_superadmin',
            field=models.BooleanField(default=False, help_text='Whether current password was set by superadmin'),
        ),
    ]