import psycopg2
from img2vec_pytorch import Img2Vec
from PIL import Image
import numpy as np
import os, sys

raiz = 'C:/GAD/TPFinal/train'


def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="pruebaPython",
        user="postgres",
        password="password")
    return conn


def agregar():
    conn = conectarAPostgres()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO prueba (nombre,numero) VALUES (%s,%s);', ["Angel", 25])
    conn.commit()


def resizeImagen(imagen):
    final_size = 224
    size = imagen.size
    ratio = float(final_size) / max(size)
    new_image_size = tuple([int(x * ratio) for x in size])
    imagen = imagen.resize(new_image_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (final_size, final_size))
    new_im.paste(imagen, ((final_size - new_image_size[0]) // 2, (final_size - new_image_size[1]) // 2))

    return new_im


def usarImg():
    print('Empezamos')
    img2vec = Img2Vec(cuda=False)
    print('img2Vec abierto')
    img = Image.open('C:/GAD/TPFinal/train/Alexandrite/alexandrite_1.jpg')
    print('imagen abierta')
    vec = img2vec.get_vec(resizeImagen(img))
    print(vec)


def compararDistancia():
    img2vec = Img2Vec(cuda=False)
    img1 = Image.open('C:/GAD/TPFinal/train/Alexandrite/alexandrite_1.jpg')
    vec1 = img2vec.get_vec(resizeImagen(img1)).tolist()
    img2 = Image.open('C:/GAD/TPFinal/train/Alexandrite/alexandrite_8.jpg')
    vec2 = img2vec.get_vec(resizeImagen(img2)).tolist()
    print(np.linalg.norm(np.array(vec1) - np.array(vec2)))


def compararDistanciaDB():
    conn = conectarAPostgres()
    cursor = conn.cursor()
    print('Conexion establecida con Postgres')
    img2vec = Img2Vec(cuda=False)
    ruta = 'C:/GAD/TPFinal/test/Alexandrite/alexandrite_6.jpg'
    imgEntrada = Image.open(ruta)
    print('Imagen de entrada: ' + ruta)
    vecE = img2vec.get_vec(resizeImagen(imgEntrada))
    cursor.execute('SELECT * FROM prueba')
    print('SELECT * FROM prueba')
    resultados = cursor.fetchall()

    print('Comparando...')
    lista = []
    for row in resultados:
        distancia = (np.linalg.norm(vecE - np.array(row[2])))
        lista.append((row[1], distancia))
    print('Mostrar los 10 mas parecidos')
    lista.sort(key=usarDistancia)
    print('Sorted: ', mostrarPorSimilitud(lista, 10))

    cursor.close()
    conn.close()


def usarDistancia(elem):
    return elem[1]


def mostrarPorSimilitud(lista, cantidad):
    listaAMostrar = lista[:cantidad]
    return listaAMostrar


def agregarImagen():
    conn = conectarAPostgres()
    cursor = conn.cursor()
    img2vec = Img2Vec(cuda=False)
    rutaImg = 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_7.jpg'
    img = Image.open(rutaImg)
    vec = img2vec.get_vec(resizeImagen(img))
    cursor.execute('INSERT INTO prueba (ruta,vector) VALUES (%s,%s);', [rutaImg, vec.tolist()])
    conn.commit()


def recorrerCarpetas(path):
    contador = 0
    listaDirectorio = os.listdir(path)
    for directorio in listaDirectorio:
        subpath = f'{path}/{directorio}'
        listaSubDirectorio = os.listdir(subpath)
        for archivo in listaSubDirectorio:
            if archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg'):
                rutaImagen = f'{subpath}/{archivo}'
                contador = contador + 1
                print(rutaImagen)
    print(f'Se encontraron {contador} imagenes')


def generarDB(path):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    img2vec = Img2Vec(cuda=False)

    listaDirectorio = os.listdir(path)
    for directorio in listaDirectorio:
        subpath = f'{path}/{directorio}'
        listaSubDirectorio = os.listdir(subpath)
        for archivo in listaSubDirectorio:
            if archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg'):
                rutaImagen = f'{subpath}/{archivo}'
            img = Image.open(rutaImagen)
            vec = img2vec.get_vec(resizeImagen(img))
            cursor.execute('INSERT INTO prueba (ruta,vector) VALUES (%s,%s);', [rutaImagen, vec.tolist()])
            print('Archivo')
        print('Directorio')
        conn.commit()

    cursor.close()
    conn.close()

#Calcular las distancias maximas para el par y el vectorPivote
#Utilizado en la seleccion incremental
def calcularDistanciaMaxima(vector1, vector2, vectorPivoteCandidato, listaPivotes):
    maximo = 0
    for pivotes in listaPivotes:
        distancia1 = np.linalg.norm(np.array(vector1) - np.array(pivotes[1]))
        distancia2 = np.linalg.norm(np.array(vector2) - np.array(pivotes[1]))
        if maximo < abs(distancia1 - distancia2):
            maximo = abs(distancia1 - distancia2)
    distancia1 = np.linalg.norm(np.array(vector1) - np.array(vectorPivoteCandidato))
    distancia2 = np.linalg.norm(np.array(vector2) - np.array(vectorPivoteCandidato))
    if maximo < abs(distancia1 - distancia2):
        maximo = abs(distancia1 - distancia2)
    return maximo


def seleccionIncremental(k, n, a):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    img2vec = Img2Vec(cuda=False)
    listaPivotes = [] #Aun no tenemos ninguno
    # Seleccionando pares
    cursor.execute('SELECT prueba1.ruta, prueba1.vector, prueba2.ruta, prueba2.vector'
                   ' FROM prueba prueba1, prueba prueba2 '
                   'WHERE prueba1.ruta not in (SELECT ruta FROM pivotes) AND'
                   ' prueba2.ruta not in (SELECT ruta FROM pivotes) '
                   'ORDER BY random() LIMIT %s', (a,))      #Es importante dejar la coma en (a,) porque esta lo hace inmutable
    pares = cursor.fetchall()

    #Creamos las listas con la primer y segunda ruta de cada par
    paresruta = []
    for rowpares in pares:
        paresruta.append(rowpares[0])
        paresruta.append(rowpares[2])


    for x in range(k):
        maximo = 0

        cursor.execute('SELECT prueba.ruta, prueba.vector'
                       ' FROM prueba'
                       ' WHERE prueba.ruta NOT IN (SELECT ruta FROM pivotes) AND'
                       ' prueba.ruta NOT IN %s'
                       ' ORDER BY random() LIMIT %s', (tuple(paresruta), n,))
        pivotescandidatos = cursor.fetchall()
        cursor.execute('SELECT ruta, vector FROM pivotes')
        listaPivotes = cursor.fetchall()
        for rowpivotes in pivotescandidatos:
            sumatoria= 0
            for row in pares:
                sumatoria += calcularDistanciaMaxima(row[1], row[3], rowpivotes[1], listaPivotes)
            if maximo < (sumatoria / a):
              maximo = (sumatoria / a)
              pivoteParaAgregar = (rowpivotes[0], rowpivotes[1])

        cursor.execute('INSERT INTO pivotes (ruta,vector) VALUES (%s,%s);', [pivoteParaAgregar[0], pivoteParaAgregar[1]])
        conn.commit()
    cursor.close()
    conn.close()

def generarFirmasFQA():
    conn = conectarAPostgres()
    cursor = conn.cursor()

    cursor.execute('SELECT ruta, vector FROM prueba')
    elementos = cursor.fetchall()

    cursor.execute('SELECT * FROM pivotes')
    listaPivotes = cursor.fetchall()

    for elemento in elementos:
       distancias = []
       for pivote in listaPivotes:
           distancias.append(np.linalg.norm( np.array(elemento[1]) - np.array(pivote[2]) ) )

       cursor.execute('INSERT INTO "firmasFQA"('
	   'ruta, "distanciaPivote1", "distanciaPivote2", "distanciaPivote3",'
       ' "distanciaPivote4", "distanciaPivote5", "distanciaPivote6", "distanciaPivote7",'
       ' "distanciaPivote8", "distanciaPivote9", "distanciaPivote10")'
	   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (elemento[0],distancias[0], distancias[1], distancias[2], distancias[3], distancias[4], distancias[5], distancias[6], distancias[7], distancias[8], distancias[9],   ))

    conn.commit()

    cursor.close()
    conn.close()


def consultaFQA(vectorEntrada, radio):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    distanciasEntrada = []
    cursor.execute('SELECT vector FROM pivotes')

    ####Prueba####
    img2vec = Img2Vec(cuda=False)
    rutaIMG = 'C:/GAD/TPFinal/test/Alexandrite/alexandrite_6.jpg'
    imgEntrada = Image.open(rutaIMG)
    print('Imagen de entrada: ' + rutaIMG)
    vectorEntrada = img2vec.get_vec(resizeImagen(imgEntrada))
    ####FinPrueba####
    listaPivotes = cursor.fetchall()
    for pivote in listaPivotes:
        distanciasEntrada.append(np.linalg.norm(vectorEntrada - np.array(pivote)))

    cursor.execute('SELECT ruta FROM "firmasFQA" '
                     'WHERE "distanciaPivote1" BETWEEN %(d1)s - %(radio)s AND %(d1)s + %(radio)s '
                     'AND "distanciaPivote2" BETWEEN %(d2)s - %(radio)s AND %(d2)s + %(radio)s '
                     'AND "distanciaPivote3" BETWEEN %(d3)s - %(radio)s AND %(d3)s + %(radio)s '
                     'AND "distanciaPivote4" BETWEEN %(d4)s - %(radio)s AND %(d4)s + %(radio)s '
                     'AND "distanciaPivote5" BETWEEN %(d5)s - %(radio)s AND %(d5)s + %(radio)s '
                     'AND "distanciaPivote6" BETWEEN %(d6)s - %(radio)s AND %(d6)s + %(radio)s  '
                     'AND "distanciaPivote7" BETWEEN %(d7)s - %(radio)s AND %(d7)s + %(radio)s '
                     'AND "distanciaPivote8" BETWEEN %(d8)s - %(radio)s AND %(d8)s + %(radio)s  '
                     'AND "distanciaPivote9" BETWEEN %(d9)s - %(radio)s AND %(d9)s + %(radio)s '
                     'AND "distanciaPivote10" BETWEEN %(d10)s - %(radio)s AND %(d10)s + %(radio)s',
                     {"radio": radio, "d1": distanciasEntrada[0], "d2": distanciasEntrada[1], "d3": distanciasEntrada[2],
                      "d4": distanciasEntrada[3], "d5": distanciasEntrada[4], "d6": distanciasEntrada[5],
                      "d7": distanciasEntrada[6], "d8": distanciasEntrada[7], "d9": distanciasEntrada[8], "d10": distanciasEntrada[9]})
    resultados = cursor.fetchall()

    cursor.execute('SELECT * FROM prueba WHERE ruta IN %s', (tuple(resultados),))
    listado = cursor.fetchall()
    contador = 0
    lista = []
    for row in listado:
        contador += 1
        distancia = (np.linalg.norm(vectorEntrada - np.array(row[2])))
        lista.append((row[1], distancia))
    print('Mostrar los 10 mas parecidos')
    lista.sort(key=usarDistancia)
    print('Sorted: ', mostrarPorSimilitud(lista, 10))

    print(contador)
    cursor.close()
    conn.close()

print('Inicio')
# recorrerCarpetas(raiz)
# usarImg()
# agregarImagen()
# generarDB(raiz)
#compararDistanciaDB()
#seleccionIncremental(10, 30, 100)
#generarFirmasFQA()
consultaFQA(0, 3)

