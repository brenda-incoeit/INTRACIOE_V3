# Generated by Django 5.1.3 on 2025-03-27 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('INVENTARIO', '0007_remove_producto_descuento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='precio_iva',
            field=models.BooleanField(default=False),
        ),
    ]
