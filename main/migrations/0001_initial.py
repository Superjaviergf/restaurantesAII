# Generated by Django 4.0 on 2021-12-28 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurante',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=150)),
                ('tipoCocina', models.CharField(max_length=50)),
                ('direccion', models.CharField(max_length=250)),
                ('precioMedio', models.FloatField()),
                ('puntuacion', models.FloatField()),
                ('horarioLunes', models.CharField(max_length=50)),
                ('horarioMartes', models.CharField(max_length=50)),
                ('horarioMiercoles', models.CharField(max_length=50)),
                ('horarioJueves', models.CharField(max_length=50)),
                ('horarioViernes', models.CharField(max_length=50)),
                ('horarioSabado', models.CharField(max_length=50)),
                ('horarioDomingo', models.CharField(max_length=50)),
                ('informacion', models.CharField(max_length=2000)),
                ('servicios', models.CharField(max_length=2000)),
            ],
        ),
    ]