# Generated by Django 5.1.3 on 2025-03-06 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0037_tipo_dte_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipo_dte',
            name='version',
            field=models.IntegerField(null=True),
        ),
    ]
