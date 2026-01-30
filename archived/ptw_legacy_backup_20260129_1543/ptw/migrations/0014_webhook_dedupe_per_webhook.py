from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ptw', '0013_permittoolboxtalk_permittoolboxtalkattendance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhookdeliverylog',
            name='dedupe_key',
            field=models.CharField(
                help_text='event+permit_id+hour for idempotency',
                max_length=255
            ),
        ),
        migrations.AddConstraint(
            model_name='webhookdeliverylog',
            constraint=models.UniqueConstraint(
                fields=('webhook', 'dedupe_key'),
                name='unique_webhook_dedupe_key'
            ),
        ),
    ]
