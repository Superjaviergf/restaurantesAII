# Generated by Django 4.0 on 2021-12-28 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_restaurante_restaurant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='restaurant',
            old_name='servicios',
            new_name='caracteristicas',
        ),
    ]