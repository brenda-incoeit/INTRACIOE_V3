# Generated by Django 5.1.3 on 2025-03-06 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dte', '0012_facturaelectronica_iva_percibido_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipo_dte',
            name='version',
            field=models.CharField(max_length=2, null=True),
        ),
    ]
