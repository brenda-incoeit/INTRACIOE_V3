# Generated by Django 5.1.3 on 2025-03-13 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0067_remove_detallefactura_descuento_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detallefactura',
            old_name='por_descuento',
            new_name='descuento',
        ),
    ]
