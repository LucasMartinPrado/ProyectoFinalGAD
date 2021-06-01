import psycopg2
from img2vec_pytorch import Img2Vec
from PIL import Image
import numpy as np
import os

#Esta es la ruta de la raiz donde esta el dataset
raiz = 'C:/GAD/TPFinal/train'


#Conexion a la DB
def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="proyectoGAD",
        user="postgres",
        password="password")
    return conn

#Conversion de imagenes a RGB con tamaño estandarizado
def resizeImagen(imagen):
    final_size = 224
    size = imagen.size
    ratio = float(final_size) / max(size)
    new_image_size = tuple([int(x * ratio) for x in size])
    imagen = imagen.resize(new_image_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (final_size, final_size))
    new_im.paste(imagen, ((final_size - new_image_size[0]) // 2, (final_size - new_image_size[1]) // 2))

    return new_im

#Insertar la ruta de una imagen y su vector caracteristico a la base de datos
def agregarImagen(rutaImg):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    img2vec = Img2Vec(cuda=False)
    img = Image.open(rutaImg)
    vec = img2vec.get_vec(resizeImagen(img))
    cursor.execute('INSERT INTO imagenes (ruta,vector) VALUES (%s,%s);', [rutaImg, vec.tolist()])
    conn.commit()

#Metodo para contar la cantidad de imagenes en un arbol de directorios
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
    print(f'Se encontraron {contador} imagenes')


#Carga todas las imagenes del dataset en la base de datos, guardando ruta y vector caracteristico
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
            cursor.execute('INSERT INTO imagenes (ruta,vector) VALUES (%s,%s);', [rutaImagen, vec.tolist()])
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


#Seleccion y cargado de los pivotes
def seleccionIncremental(k, n, a):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    img2vec = Img2Vec(cuda=False)
    listaPivotes = [] #Aun no tenemos ninguno
    # Seleccionando pares
    cursor.execute('SELECT imagenes1.ruta, imagenes1.vector, imagenes2.ruta, imagenes2.vector'
                   ' FROM imagenes imagenes1, imagenes imagenes2 '
                   'WHERE imagenes1.ruta not in (SELECT ruta FROM pivotes) AND'
                   ' imagenes2.ruta not in (SELECT ruta FROM pivotes) '
                   'ORDER BY random() LIMIT %s', (a,))
    pares = cursor.fetchall()

    #Creamos las listas con la primer y segunda ruta de cada par
    paresruta = []
    for rowpares in pares:
        paresruta.append(rowpares[0])
        paresruta.append(rowpares[2])

    for x in range(k):
        maximo = 0

        cursor.execute('SELECT imagenes.ruta, imagenes.vector'
                       ' FROM imagenes'
                       ' WHERE imagenes.ruta NOT IN (SELECT ruta FROM pivotes) AND'
                       ' imagenes.ruta NOT IN %s'
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


#Genera y carga todas las firmas de los elementos a la tabla de firmas
def generarFirmasFQA():
    conn = conectarAPostgres()
    cursor = conn.cursor()

    #Obtenemos los elementos de la base de datos
    cursor.execute('SELECT ruta, vector FROM imagenes')
    elementos = cursor.fetchall()

    #Obtenemos los pivotes
    cursor.execute('SELECT * FROM pivotes')
    listaPivotes = cursor.fetchall()

    for elemento in elementos:
       distancias = []
       for pivote in listaPivotes:
           distancias.append(np.linalg.norm(np.array(elemento[1]) - np.array(pivote[2])))

       cursor.execute('INSERT INTO "firmasFQA"('
	   'ruta, "distanciaPivote1", "distanciaPivote2", "distanciaPivote3",'
       ' "distanciaPivote4", "distanciaPivote5", "distanciaPivote6", "distanciaPivote7",'
       ' "distanciaPivote8", "distanciaPivote9", "distanciaPivote10")'
	   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (elemento[0],distancias[0], distancias[1], distancias[2], distancias[3], distancias[4], distancias[5], distancias[6], distancias[7], distancias[8], distancias[9],   ))

    conn.commit()
    cursor.close()
    conn.close()

#Cargado de la base de datos
generarDB(raiz)
#seleccionIncremental(10, 30, 100)
generarFirmasFQA()

