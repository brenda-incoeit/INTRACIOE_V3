# Generated by Django 5.1.3 on 2025-04-22 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0111_remove_eventocontingencia_h_inicio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventocontingencia',
            name='h_inicio',
            field=models.TimeField(auto_now_add=True, null=True),
        ),
    ]
