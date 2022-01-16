from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    nombre = models.CharField(max_length=150, primary_key=True)
    tipoCocina = models.CharField(max_length=100, null=True)
    direccion = models.CharField(max_length=250, null=True)
    precioMedio = models.FloatField(null=True)
    puntuacion = models.FloatField(null=True)
    horarioLunes = models.CharField(max_length=50, null=True)
    horarioMartes = models.CharField(max_length=50, null=True)
    horarioMiercoles = models.CharField(max_length=50, null=True)
    horarioJueves = models.CharField(max_length=50, null=True)
    horarioViernes = models.CharField(max_length=50, null=True)
    horarioSabado = models.CharField(max_length=50, null=True)
    horarioDomingo = models.CharField(max_length=50, null=True)
    informacion = models.TextField(null=True)
    caracteristicas = models.TextField(null=True)
    url = models.URLField(validators=[URLValidator()], null=True)

    def __str__(self):
        return self.nombre


class Opinion(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING)
    texto = models.CharField(max_length=3000, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return str(self.user.username) + ' | ' + str(self.restaurant.nombre) + ' | ' + str(self.rating)
