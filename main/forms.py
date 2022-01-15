from django import forms
from django.db.models import Count

from main.models import User, Opinion, Restaurant


class GeneralRestaurantForm(forms.Form):
    general = forms.CharField(label='Introduzca la búsqueda')


class TipoCocinaRestaurantForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TipoCocinaRestaurantForm, self).__init__(*args, **kwargs)
        tiposCocina = set()
        for restaurant in Restaurant.objects.all():
            tipos = [(tipo.strip(), tipo.strip()) for tipo in restaurant.tipoCocina.split(',')]
            tiposCocina.update(tipos)

        self.fields['tipoCocina'] = forms.ChoiceField(choices=tiposCocina, label='Introduzca el tipo o los tipos de cocina')


class ServicioRestaurantForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ServicioRestaurantForm, self).__init__(*args, **kwargs)
        servicios = set()
        for restaurant in Restaurant.objects.all():
            caracteristicas = [(caracteristica.strip(), caracteristica.strip()) for caracteristica in restaurant.caracteristicas.split(',')]
            servicios.update(caracteristicas)

        self.fields['servicio'] = forms.ChoiceField(choices=servicios, label='Introduzca el servicio o servicios')


class PrecioMenorIgualForm(forms.Form):
    precio = forms.FloatField(label='Introduzca el límite de precio a buscar')


class UserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        ratingsAgrupados = Opinion.objects.values('user__username').annotate(dcount=Count('user__username')).order_by()
        listaUsuariosValidos = [(rating['user__username'], rating['user__username']) for rating in list(filter(lambda e: e['dcount'] >= 7, ratingsAgrupados))]

        # for u in User.objects.all():
        #     username = u.username
        #     ratings = Opinion.objects.filter(user=u)
        #     if len(ratings) >= 7:
        #         listaUsuariosValidos.append((username, username))
        #
        # listaUsuariosValidos.sort()

        self.fields['user'] = forms.ChoiceField(choices=listaUsuariosValidos, label='Seleccione un usuario')
