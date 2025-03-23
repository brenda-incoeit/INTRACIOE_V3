# Generated by Django 5.1.7 on 2025-03-22 18:34

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FE', '0069_remove_detallefactura_base_imponible_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventoContingencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_generacion', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('fecha_transmicion', models.DateField(auto_now_add=True, null=True)),
                ('hora_transmision', models.TimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='facturaelectronica',
            name='documento_relacionado',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
