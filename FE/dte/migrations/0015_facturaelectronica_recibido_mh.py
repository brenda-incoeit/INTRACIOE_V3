# Generated by Django 5.1.3 on 2025-03-06 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dte', '0014_alter_tipo_dte_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturaelectronica',
            name='recibido_mh',
            field=models.BooleanField(default=False),
        ),
    ]
