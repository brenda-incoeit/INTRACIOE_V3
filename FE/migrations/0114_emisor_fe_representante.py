# Generated by Django 5.1.3 on 2025-04-22 16:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0113_representanteemisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='emisor_fe',
            name='representante',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='FE.representanteemisor'),
        ),
    ]
