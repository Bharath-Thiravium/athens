from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ptw', '0015_rename_ptw_isolati_project_idx_ptw_isolati_project_348eb9_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permit',
            name='qr_code',
            field=models.TextField(blank=True),
        ),
    ]
