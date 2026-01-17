from django.db import migrations


def backfill_project_tenant_id(apps, schema_editor):
    Project = apps.get_model('authentication', 'Project')
    CustomUser = apps.get_model('authentication', 'CustomUser')

    master_users = CustomUser.objects.filter(
        athens_tenant_id__isnull=False,
        user_type__in=['master', 'masteradmin'],
    ).values_list('athens_tenant_id', flat=True)
    admin_type_master_users = CustomUser.objects.filter(
        athens_tenant_id__isnull=False,
        admin_type__in=['master', 'masteradmin'],
    ).values_list('athens_tenant_id', flat=True)

    tenant_ids = set(master_users) | set(admin_type_master_users)
    if len(tenant_ids) != 1:
        return

    tenant_id = next(iter(tenant_ids))
    Project.objects.filter(athens_tenant_id__isnull=True).update(athens_tenant_id=tenant_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0011_menumodule_description_alter_customuser_user_type'),
    ]

    operations = [
        migrations.RunPython(backfill_project_tenant_id, noop_reverse),
    ]
