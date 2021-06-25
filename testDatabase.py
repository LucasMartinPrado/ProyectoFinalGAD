import os
from metodos import *
from skimage.transform import resize
from skimage import io
import matplotlib.pyplot as plt


#Raiz de la carpeta de testing
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
    return contador


#Realiza la consulta usando la tabla FQA
#Similar al de metodos.py, pero ligeramente modificado para realizar pruebas
def consultaFQAPruebas(nombreDB, ruta, radio):
    conn = None
    try:
        conn = conectarAPostgresPruebas(nombreDB)
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


#Muestra en pantalla la imagen, la imagen con la mascara aplicada
#y los histogramas de colores: totales, canal rojo, canal verde, y canal azul.
def histogram():
    image = resize(io.imread('C:/GAD/TPFinal/test/moonstone/moonstone_18.jpg'), (224, 224))
    io.imshow(image)
    plt.show()
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

    _ = plt.hist(image[:, :, 0].ravel(), bins=32)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()

    _ = plt.hist(image[:, :, 1].ravel(), bins=32)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()

    _ = plt.hist(image[:, :, 2].ravel(), bins=32)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    plt.show()




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
                print('Imagen ' + str(contador) + ' de ' + str(totalImagenesPrueba))
                rutaImagen = f'{subpath}/{archivo}'
                resultadoEsperado = rutaImagen.split("/")[-2]
                lista = mostrarPorSimilitud(consultaFQAPruebas(nombreDB, rutaImagen, 1000000), 10)
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
    return (aciertos)














print('Inicio')
#recorrerCarpetas(raiz)
#consultaFQA(0, 3)
#histogram()
print(pruebaTasaAcierto("proyectoGAD"))

