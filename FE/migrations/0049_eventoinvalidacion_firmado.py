# Generated by Django 5.1.3 on 2025-03-07 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0048_eventoinvalidacion_json_firmado'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventoinvalidacion',
            name='firmado',
            field=models.BooleanField(default=False),
        ),
    ]
