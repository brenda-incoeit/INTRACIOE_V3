# Generated by Django 5.1.3 on 2025-03-04 17:19

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dte', '0003_rename_ambiene_emisor_fe_ambiente'),
    ]

    operations = [
        migrations.AddField(
            model_name='numerocontrol',
            name='tipo_dte',
            field=models.CharField(default=uuid.uuid4, max_length=2, unique=True),
        ),
    ]
