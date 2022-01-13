from django import forms

from main.models import User, Opinion


class GeneralRestaurantForm(forms.Form):
    general = forms.CharField(label='Introduzca la búsqueda')


class TipoCocinaRestaurantForm(forms.Form):
    tipoCocina = forms.CharField(label='Introduzca el tipo o los tipos de cocina')


class ServicioRestaurantForm(forms.Form):
    servicio = forms.CharField(label='Introduzca el servicio o servicios')


class PrecioMenorIgualForm(forms.Form):
    precio = forms.FloatField(label='Introduzca el límite de precio a buscar')


class UserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        listaUsuariosValidos = []
        for u in User.objects.all():
            username = u.username
            ratings = Opinion.objects.filter(user=u)
            if len(ratings) >= 7:
                listaUsuariosValidos.append((username, username))

        listaUsuariosValidos.sort()
        self.fields['user'] = forms.ChoiceField(choices=listaUsuariosValidos, label='Seleccione un usuario')
