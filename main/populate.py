# lineas para evitar error SSL
import os
import re
import shutil
import ssl
import urllib.request

from datetime import datetime

import numpy as numpy
from bs4 import BeautifulSoup
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser

from main.models import Restaurant, User, Opinion

nombresRestaurantes = set()

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def url_habilitada(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    f = urllib.request.urlopen(req).read()
    s = BeautifulSoup(f, "html.parser")

    return s


def deleteTables():
    Opinion.objects.all().delete()
    Restaurant.objects.all().delete()
    User.objects.all().delete()


def extraer_restaurantes():
    # devuelve una tupla de listas. Cada lista tiene la información requerida de un restaurante, usuarios y ratings
    restaurantes = ([], [], [])
    nombresRestaurantes.clear()

    for i in range(1, 11):
        if i == 1:
            lista_sevilla = extraer_pagina("https://es.restaurantguru.com/Seville")
        else:
            lista_sevilla = extraer_pagina("https://es.restaurantguru.com/Seville/" + str(i))

        restaurantes[0].extend(lista_sevilla[0])
        restaurantes[1].extend(lista_sevilla[1])
        restaurantes[2].extend(lista_sevilla[2])

    return restaurantes


def extraer_pagina(url):
    restaurantes = []
    users = set()
    ratings = []

    s = url_habilitada(url)
    l = s.find_all("div", class_='restaurant_row')  # lista de restaurantes de la pagina

    for i in l:
        nombre = i.a.string

        if nombre not in nombresRestaurantes:
            nombresRestaurantes.add(nombre)
            d = url_habilitada(i.a['href'])

            if d.find("div", class_='cuisine_wrapper'):
                tipoCocina = d.find("div", class_='cuisine_wrapper').text.replace('\n', '')
            else:
                tipoCocina = 'No definido'

            if d.find("div", class_='address'):
                direccion = d.find("div", class_='address').findChildren()[1].text.replace('\n', '')
            else:
                direccion = None

            if d.find("div", class_='with_avg_price'):
                rangoPrecios = d.find("div", class_='with_avg_price').find("span", class_='text_overflow').string \
                    .replace('Rango de precios por persona ', '').replace('€', '').replace('-', '').split()
                try:
                    precioMedio = (int(rangoPrecios[0]) + int(rangoPrecios[1])) / 2
                except:
                    precioMedio = None
            else:
                precioMedio = None

            if d.find("div", class_='work_time'):
                horario = d.find("div", class_='work_time').find("table").findAll("tr")

                horarios = []
                for h in horario:
                    horas = h.findAll("td")[1].text

                    if len(horas) > 11:
                        horas = horas[:11] + '\n' + horas[11:]

                    dato = str(horas)
                    horarios.append(dato)
            else:
                horarios = [None, None, None, None, None, None, None]

            if d.find("div", class_='right_column_wrapper').find("div", class_="website"):
                url = d.find("div", class_='right_column_wrapper').find("div", class_="website").a['href']
            else:
                url = None

            informacion = d.find("div", class_='description').text.replace('\n', '')

            if d.find("div", class_='features_block'):
                featuresList = d.find("div", class_='features_block').findAll("span", class_='feature_item')

                featuresNone = []
                if d.find("div", class_='features_block').findAll("span", class_='none'):
                    featuresNone = [feat.text for feat in
                                    d.find("div", class_='features_block').findAll("span", class_='none')]
            else:
                featuresList = []

            caracteristicas = ''
            firstFeature = True
            for feature in featuresList:
                if feature.text not in featuresNone:
                    if firstFeature:
                        firstFeature = False
                        caracteristicas += feature.text
                    else:
                        caracteristicas += ', ' + feature.text

            restaurante = {'nombre': nombre, 'tipoCocina': tipoCocina, 'direccion': direccion, 'precioMedio': precioMedio,
                           'horarios': horarios, 'informacion': informacion,
                           'caracteristicas': caracteristicas, 'url': url}

            print('Recuperado restaurante: ' + str(restaurante))

            restaurantes.append(restaurante)

            estrellasParaMedia = []

            if d.find("div", {'id': 'comments_container'}).find("a", class_='show_all'):
                c = url_habilitada(d.find("div", {'id': 'comments_container'}).find("a", class_='show_all')['href'])
                listaComentarios = c.findAll("div", class_='o_review')
            else:
                listaComentarios = d.findAll("div", class_='o_review')

            for com in listaComentarios:
                userInfo = com.find("div", class_='user_info')
                if userInfo and userInfo.find("span", class_='stars'):
                    if userInfo.a:
                        username = userInfo.a.text
                    else:
                        username = userInfo.string
                    if username is None:
                        username = 'A Google User'

                    print(username)
                    users.add(str(username))

                    stars = float(userInfo.find("span", class_='stars').find("span")['style'].replace('width: ', '').replace('%', '').replace(';', '')) * 5 / 100
                    estrellasParaMedia.append(stars)

                    if com.find("span", class_='text_full'):
                        comentario = com.find("span", class_='text_full').string
                    else:
                        comentario = None

                    rating = {'stars': stars, 'texto': comentario, 'user': username, 'restaurante': nombre}

                    print(rating)
                    ratings.append(rating)

            if len(estrellasParaMedia) > 0:
                restaurante['puntuacion'] = numpy.round(numpy.mean(estrellasParaMedia), 1)
            else:
                restaurante['puntuacion'] = None

    return (restaurantes, users, ratings)


def almacenar_datos():
    # define el esquema de la información
    schem = Schema(nombre=TEXT(stored=True), tipoCocina=TEXT(stored=True),
                   direccion=TEXT(stored=True), precioMedio=NUMERIC(stored=True, numtype=float),
                   puntuacion=NUMERIC(stored=True, numtype=float),
                   horarioLunes=TEXT(stored=True), horarioMartes=TEXT(stored=True), horarioMiercoles=TEXT(stored=True),
                   horarioJueves=TEXT(stored=True), horarioViernes=TEXT(stored=True), horarioSabado=TEXT(stored=True),
                   horarioDomingo=TEXT(stored=True),
                   informacion=TEXT, caracteristicas=TEXT(stored=True), url=TEXT(stored=True))

    # eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    # creamos el índice
    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i = 0
    tupla = extraer_restaurantes()

    listaRestaurantes = []
    for restaurante in tupla[0]:
        print('Añadiendo restaurante: ' + str(restaurante))

        # añade cada noticia de la lista al índice
        writer.add_document(nombre=str(restaurante['nombre']), tipoCocina=str(restaurante['tipoCocina']),
                            direccion=str(restaurante['direccion']), precioMedio=restaurante['precioMedio'],
                            puntuacion=restaurante['puntuacion'],
                            horarioLunes=str(restaurante['horarios'][0]), horarioMartes=str(restaurante['horarios'][1]),
                            horarioMiercoles=str(restaurante['horarios'][2]),
                            horarioJueves=str(restaurante['horarios'][3]),
                            horarioViernes=str(restaurante['horarios'][4]),
                            horarioSabado=str(restaurante['horarios'][5]),
                            horarioDomingo=str(restaurante['horarios'][6]),
                            informacion=str(restaurante['informacion']), caracteristicas=restaurante['caracteristicas'],
                            url=str(restaurante['url']))

        r = Restaurant(nombre=str(restaurante['nombre']), tipoCocina=str(restaurante['tipoCocina']),
                       direccion=str(restaurante['direccion']), precioMedio=restaurante['precioMedio'],
                       puntuacion=restaurante['puntuacion'],
                       horarioLunes=str(restaurante['horarios'][0]), horarioMartes=str(restaurante['horarios'][1]),
                       horarioMiercoles=str(restaurante['horarios'][2]),
                       horarioJueves=str(restaurante['horarios'][3]),
                       horarioViernes=str(restaurante['horarios'][4]),
                       horarioSabado=str(restaurante['horarios'][5]),
                       horarioDomingo=str(restaurante['horarios'][6]),
                       informacion=str(restaurante['informacion']), caracteristicas=restaurante['caracteristicas'],
                       url=str(restaurante['url']))

        listaRestaurantes.append(r)

        i += 1
    writer.commit()
    Restaurant.objects.bulk_create(listaRestaurantes)

    usuarios = []
    for user in set(tupla[1]):
        u = User(username=user)
        usuarios.append(u)
    User.objects.bulk_create(usuarios)

    opiniones = []
    for opinion in tupla[2]:
        o = Opinion(user=User.objects.get(username=opinion['user']),
                    restaurant=Restaurant.objects.get(nombre=opinion['restaurante']),
                    rating=opinion['stars'], texto=opinion['texto'])
        opiniones.append(o)
    Opinion.objects.bulk_create(opiniones)
