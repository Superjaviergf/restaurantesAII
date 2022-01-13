import shelve

from django.shortcuts import render, get_object_or_404

#  CONJUNTO DE VISTAS
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser

from main.forms import GeneralRestaurantForm, TipoCocinaRestaurantForm, ServicioRestaurantForm, PrecioMenorIgualForm, \
    UserForm
from main.models import Restaurant, User, Opinion
from main.populate import almacenar_datos, extraer_pagina, extraer_restaurantes, deleteTables
from main.recommendations import getRecommendations, transformPrefs


def index(request):
    return render(request, 'index.html')


def confirmPopulate(request):
    return render(request, 'confirmarPopulate.html')


def populate(request):
    deleteTables()
    almacenar_datos()
    return render(request, 'loadComplete.html')


def findAll(request):
    restaurantes = Restaurant.objects.all()
    return render(request, 'findAll.html', {'restaurantes': restaurantes})


def search(request):
    if request.method == 'GET':
        form = GeneralRestaurantForm(request.GET, request.FILES)
        if form.is_valid():
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                general = form.cleaned_data['general']
                query = MultifieldParser(
                    ["nombre", "tipoCocina", "direccion", "precioMedio", "puntuacion", "horarioLunes", "horarioMartes",
                     "horarioMiercoles", "horarioJueves", "horarioViernes", "horarioSabado", "horarioDomingo",
                     "informacion", "caracteristicas"], ix.schema).parse(general)
                restaurantes = searcher.search(query, limit=None)
                return render(request, 'busquedaGeneral.html', {'restaurantes': restaurantes, 'form': form,
                                                                'titulo': 'Búsqueda general de Restaurantes'})
    form = GeneralRestaurantForm()
    return render(request, 'searchView.html', {'form': form, 'titulo': 'Búsqueda general de Restaurantes'})


def searchByCocina(request):
    if request.method == 'GET':
        form = TipoCocinaRestaurantForm(request.GET, request.FILES)
        if form.is_valid():
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                tipoCocina = form.cleaned_data['tipoCocina']
                query = QueryParser("tipoCocina", ix.schema).parse(tipoCocina)
                restaurantes = searcher.search(query, limit=None)
                return render(request, 'busquedaGeneral.html', {'restaurantes': restaurantes, 'form': form,
                                                                'titulo': 'Búsqueda por tipos de cocina'})
    form = TipoCocinaRestaurantForm()
    return render(request, 'searchView.html', {'form': form, 'titulo': 'Búsqueda por tipos de cocina'})


def searchByServicios(request):
    if request.method == 'GET':
        form = ServicioRestaurantForm(request.GET, request.FILES)
        if form.is_valid():
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                servicio = form.cleaned_data['servicio']
                query = QueryParser("caracteristicas", ix.schema).parse(servicio)
                restaurantes = searcher.search(query, limit=None)
                return render(request, 'busquedaGeneral.html', {'restaurantes': restaurantes, 'form': form,
                                                                'titulo': 'Búsqueda por servicios'})
    form = ServicioRestaurantForm()
    return render(request, 'searchView.html', {'form': form, 'titulo': 'Búsqueda por servicios'})


def searchByPrecio(request):
    if request.method == 'GET':
        form = PrecioMenorIgualForm(request.GET, request.FILES)
        if form.is_valid():
            precio = form.cleaned_data['precio']
            restaurantes = Restaurant.objects.filter(precioMedio__lte=precio)
            return render(request, 'busquedaGeneral.html',
                          {'restaurantes': restaurantes, 'form': form, 'titulo': 'Búsqueda por precios'})
    form = PrecioMenorIgualForm()
    return render(request, 'searchView.html', {'form': form, 'titulo': 'Búsqueda por precios'})


# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a restaurantes. Tambien carga el diccionario inverso
# Serializa los resultados en dataRS.dat
def loadDict():
    Prefs = {}  # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    ratings = Opinion.objects.all()
    for ra in ratings:
        user = str(ra.user.pk)
        itemPk = str(ra.restaurant.pk)
        rating = float(ra.rating)
        Prefs.setdefault(user, {})
        Prefs[user][itemPk] = rating
    shelf['Prefs'] = Prefs
    shelf['ItemsPrefs'] = transformPrefs(Prefs)
    shelf.close()


def confirmLR(request):
    return render(request, 'confirmarLR.html')


def loadRS(request):
    loadDict()
    return render(request, 'loadComplete.html')


def recommendedRestaurantUser(request):
    if request.method == 'GET':
        form = UserForm(request.GET, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['user']
            user = get_object_or_404(User, pk=username)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            rankings = getRecommendations(Prefs, str(username))
            recommended = rankings[:20]
            restaurantes = []
            scores = []
            for re in recommended:
                restaurantes.append(Restaurant.objects.get(pk=re[1]))
                scores.append(re[0])
            items = zip(restaurantes, scores)
            return render(request, 'datosRecomendacion.html', {'user': user, 'items': items, 'form': form})
        else:
            form = UserForm()
    return render(request, 'recommendationView.html', {'form': form})
