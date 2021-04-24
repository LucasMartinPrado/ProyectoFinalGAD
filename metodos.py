import psycopg2
from img2vec_pytorch import Img2Vec
from PIL import Image
import numpy as np

raiz = 'C:/GAD/TPFinal/train'

#Conexion a la DB
def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="pruebaPython",
        user="postgres",
        password="password")
    return conn

#Conversion de imagenes a RGB y modificacion del tamaño, manteniendo relacion de aspecto
def resizeImagen(imagen):
    final_size = 224
    size = imagen.size
    ratio = float(final_size) / max(size)
    new_image_size = tuple([int(x * ratio) for x in size])
    imagen = imagen.resize(new_image_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (final_size, final_size))
    new_im.paste(imagen, ((final_size - new_image_size[0]) // 2, (final_size - new_image_size[1]) // 2))

    return new_im


#Obtener el vector de una imagen a partir de una Ruta, por ejemplo: 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_1.jpg'
def obtenerVectorImagen(rutaImagen):
    img2vec = Img2Vec(cuda=False)
    img = Image.open(rutaImagen)
    vec = img2vec.get_vec(resizeImagen(img))
    return vec

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


def consultaFQA(vectorEntrada, radio):
    conn = conectarAPostgres()
    cursor = conn.cursor()
    distanciasEntrada = []
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
    cursor.execute('SELECT * FROM prueba WHERE ruta IN %s', (tuple(resultados),))
    listado = cursor.fetchall()

    #Armamos la lista de rutas y distancias
    lista = []
    for row in listado:
        distancia = (np.linalg.norm(vectorEntrada - np.array(row[2])))
        lista.append((row[1], distancia))

    #Ordenamos la lista por distancia
    lista.sort(key=usarDistancia)

    cursor.close()
    conn.close()
    return lista

print('Inicio')
ruta = 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_7.jpg'
imagen = Image.open(ruta)
v = obtenerVectorImagen(ruta)
lista = consultaFQA(v, 3)
print(mostrarPorSimilitud(lista, 10))

