import psycopg2
from img2vec_pytorch import Img2Vec
from PIL import Image
import numpy as np
import os, sys
from metodos import *
from skimage.transform import resize
from skimage import io, data
import matplotlib.pyplot as plt
from skimage.viewer import ImageViewer


raiz = 'C:/GAD/TPFinal/test'

#Metodo para acceder a la base de datos
#Ligeramente modificado para realizar pruebas
def conectarAPostgresPruebas(nombreDB):
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database=nombreDB,
        user="postgres",
        password="password")
    return conn


def resizeImagen(imagen):
    final_size = 224
    size = imagen.size
    ratio = float(final_size) / max(size)
    new_image_size = tuple([int(x * ratio) for x in size])
    imagen = imagen.resize(new_image_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (final_size, final_size))
    new_im.paste(imagen, ((final_size - new_image_size[0]) // 2, (final_size - new_image_size[1]) // 2))

    return new_im

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
                print(rutaImagen.split("/")[-2])
    print(f'Se encontraron {contador} imagenes')


#Realiza la consulta usando la tabla FQA
#Similar al de metodos.py, pero ligeramente modificado para realizar pruebas
def consultaFQAPruebas(nombreDB, ruta, radio):
    conn = None
    try:
        conn = conectarAPostgresPruebas(nombreDB)
        cursor = conn.cursor()
        distanciasEntrada = []
        vectorEntrada = obtenerVectorImagenPrueba(ruta)
        #Obtenemos los pivotes
        cursor.execute('SELECT vector FROM pivotes')
        listaPivotes = cursor.fetchall()
        #Obtenemos el vector de firmas de la imagen de entrada
        for pivote in listaPivotes:
            distanciasEntrada.append(np.linalg.norm(vectorEntrada - np.array(pivote)))

        #Filtramos aquellos elementos que no se encuentren en el radio de busqueda
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

        #Obtenemos los vectores que pasaron el filtro
        cursor.execute('SELECT * FROM imagenes WHERE ruta IN %s', (tuple(resultados),))
        listado = cursor.fetchall()

        #Armamos la lista de rutas y distancias
        lista = []
        for row in listado:
            distancia = (np.linalg.norm(vectorEntrada - np.array(row[2])))
            #Verificamos que el elemento este dentro del radio de consulta
            if distancia < radio:
             lista.append((row[1], distancia))

        #Ordenamos la lista por distancia
        lista.sort(key=usarDistancia)

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            return lista



def histogram():
    image = resize(io.imread('C:/GAD/TPFinal/test/moonstone/moonstone_18.jpg'), (224, 224))
    image = maskTImagen(image)
    io.imshow(image)
    plt.show()

    _ = plt.hist(image.ravel(), bins=4, color='orange', )
    _ = plt.hist(image[:, :, 0].ravel(), bins=16, color='red', alpha=0.5)
    _ = plt.hist(image[:, :, 1].ravel(), bins=16, color='Green', alpha=0.5)
    _ = plt.hist(image[:, :, 2].ravel(), bins=16, color='Blue', alpha=0.5)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    _ = plt.legend(['Total', 'Red_Channel', 'Green_Channel', 'Blue_Channel'])
    plt.show()
    Output: Figure - 2

    _ = plt.hist(image[:, :, 0].ravel(), bins=16)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()
    Output: Figure - 3

    _ = plt.hist(image[:, :, 1].ravel(), bins=16)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()
    Output: Figure - 4

    _ = plt.hist(image[:, :, 2].ravel(), bins=16)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()
    Output: Figure - 5




#Este metodo compara los resultados de las consultasFQA con lo esperado
#Aciertos = [Tres primeros, Cinco primeros, Diez primeros]
def pruebaTasaAcierto(nombreDB):
    #Obtenemos el total de imagenes
    totalImagenesPrueba = recorrerCarpetas(raiz)
    aciertos = [0, 0, 0]

    #Comenzamos a recorrer la carpeta de pruebas
    contador = 0
    listaDirectorio = os.listdir(raiz)
    for directorio in listaDirectorio:
        subpath = f'{raiz}/{directorio}'
        listaSubDirectorio = os.listdir(subpath)
        for archivo in listaSubDirectorio:
            if archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg'):
                contador += 1
                print(contador)
                rutaImagen = f'{subpath}/{archivo}'
                resultadoEsperado = rutaImagen.split("/")[-2]
                lista = mostrarPorSimilitud(consultaFQAPruebas(nombreDB, rutaImagen, 1000), 10)
                #Recorremos los resultados
                sinResultado = True
                i = 0
                while sinResultado and (i < len(lista)):
                    resultadoObtenido = lista[i][0].split("/")[-2]
                    if resultadoEsperado == resultadoObtenido:
                    #Si esta entre los tres primeros
                        if i < 3:
                            aciertos[0] += 1
                            aciertos[1] += 1
                            aciertos[2] += 1
                        else:
                            #Si esta entre los cinco primeros
                            if i < 5:
                               aciertos[1] += 1
                               aciertos[2] += 1
                            else:
                               #Esta entre los diez primeros
                               aciertos[2] += 1
                        #Tenemos resultado, por lo que actualizamos la condicion de salida
                        sinResultado = False
                    #Incrementamos el indice
                    i += 1
    return aciertos














print('Inicio')
#recorrerCarpetas(raiz)
#consultaFQA(0, 3)
histogram()
#print(pruebaTasaAcierto("proyectoGADPruebaN"))

