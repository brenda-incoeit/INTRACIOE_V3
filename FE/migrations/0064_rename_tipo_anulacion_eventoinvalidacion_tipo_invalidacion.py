# Generated by Django 5.1.3 on 2025-03-13 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0063_remove_tributo_tipo_tributo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventoinvalidacion',
            old_name='tipo_anulacion',
            new_name='tipo_invalidacion',
        ),
    ]
