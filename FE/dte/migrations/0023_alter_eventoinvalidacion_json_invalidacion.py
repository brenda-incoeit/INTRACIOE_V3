# Generated by Django 5.1.3 on 2025-03-07 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dte', '0022_rename_json_original_eventoinvalidacion_json_invalidacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoinvalidacion',
            name='json_invalidacion',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
