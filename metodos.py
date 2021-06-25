import psycopg2
from img2vec_pytorch import Img2Vec
from PIL import Image
import numpy as np
import skimage
from skimage import io, filters, color
from skimage.transform import resize
import matplotlib.pyplot as plt

#Raiz de la carpeta de entrenamiento
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

#Normaliza cualquier vector
def normalizar(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

#Normaliza el vector de colores,
#ademas elimina los dos bordes del histograma (filtrando mascaras)
#y aumenta el peso para la funcion ponderada de distancia en 5^2.
def normalizarColores(vector):
    vector = vector[1:len(vector)-1]
    return 5 * normalizar(vector)

#Aplica la mascara a la imagen
def maskTImagen(image):
    #Parametros internos:
    sigma = 2
    #Lo pasamos a grises y difuminamos
    blur = skimage.color.rgb2gray(image)
    blur = skimage.filters.gaussian(blur, sigma=sigma)
    #Verificamos el color predominante del fondo (Blanco o Negro)
    fondoBlanco = False
    histograma = plt.hist(image.ravel(), bins=4)
    if histograma[0][3] > histograma[0][1] and histograma[0][3] > histograma[0][0]:
        fondoBlanco = True
    #Usamos metodo de Otsu para determinar el valor limite
    t = skimage.filters.threshold_otsu(blur)
    if fondoBlanco:
        mask = blur < t
    else:
        mask = blur > t
    #Con la mask seleccionamos lo relevante y lo devolvemos
    sel = np.zeros_like(image)
    sel[mask] = image[mask]
    return sel


#Obtener el vector de una imagen a partir de una Ruta, por ejemplo: 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_1.jpg'
def obtenerVectorImagen(rutaImagen):
    #Obtenemos la primera parte del vector a partir de Img2Vec
    img2vec = Img2Vec(cuda=False)
    img = Image.open(rutaImagen)
    vec = img2vec.get_vec(resizeImagen(img)) #Vector img2vec
    #Obtenemos la segunda parte del vector, los colores separados en RGB
    image = resize(io.imread(rutaImagen), (224, 224))
    image = maskTImagen(image)
    #Canal rojo
    vecHistograma = plt.hist(image[:, :, 0].ravel(), bins=32)
    r = normalizarColores(np.array(vecHistograma[0])) #Vector del canal rojo
    #Canal verde
    vecHistograma = plt.hist(image[:, :, 1].ravel(), bins=32)
    g = normalizarColores(np.array(vecHistograma[0])) #Vector del canal verde
    #Canal azul
    vecHistograma = plt.hist(image[:, :, 2].ravel(), bins=32)
    b = normalizarColores(np.array(vecHistograma[0])) #Vector del canal azul
    #Concatenamos y devolvemos el resultado
    vecResultante = np.around(np.concatenate((vec, r, g, b)), 4)
    return vecResultante

#Selecciona el segundo elemento del array para usar como criterio de ordenamiento
def usarDistancia(elem):
    return elem[1]

#Muestra cierta cantidad de elementos de una lista
def mostrarPorSimilitud(lista, cantidad):
    listaAMostrar = lista[:cantidad]
    return listaAMostrar

#Agrega una imagen a la BD
def agregarImagen():
    conn = None
    try:
        conn = conectarAPostgres()
        cursor = conn.cursor()
        rutaImg = 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_7.jpg'
        vec = obtenerVectorImagen(rutaImg)
        cursor.execute('INSERT INTO imagenes (ruta,vector) VALUES (%s,%s);', [rutaImg, vec.tolist()])
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#Realiza la consulta usando la tabla FQA
def consultaFQA(ruta, radio):
    conn = None
    lista = []
    try:
        conn = conectarAPostgres()
        cursor = conn.cursor()
        distanciasEntrada = []
        vectorEntrada = obtenerVectorImagen(ruta)
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
