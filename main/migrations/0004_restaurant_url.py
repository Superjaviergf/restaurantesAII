# Generated by Django 4.0 on 2021-12-28 19:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rename_servicios_restaurant_caracteristicas'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='url',
            field=models.URLField(null=True, validators=[django.core.validators.URLValidator()]),
        ),
    ]