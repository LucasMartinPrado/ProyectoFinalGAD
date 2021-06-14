import os
from metodos import *
import psycopg2
import numpy as np

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


#Metodo para contar la cantidad de imagenes en un arbol de directorios
def recorrerCarpetas(path):
    contador = 0
    listaDirectorio = os.listdir(path)
    for directorio in listaDirectorio:
        subpath = f'{path}/{directorio}'
        listaSubDirectorio = os.listdir(subpath)
        for archivo in listaSubDirectorio:
            if archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg'):
                contador = contador + 1
    print(f'Se encontraron {contador} imagenes')

#Crea las tablas de la base de datos
def crearTablas(conn, cursor):
    commands = (
        """
        CREATE TABLE IF NOT EXISTS public.imagenes
            (
                id serial,
                ruta character varying,
                vector real[],
                PRIMARY KEY (id)
            )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.pivotes
            (
                idPivote serial,
                ruta character varying,
                vector real[],
                PRIMARY KEY (idPivote, ruta)
            )
        """,
        """
        CREATE TABLE IF NOT EXISTS public."firmasFQA" 
        (
            ruta character varying NOT NULL,
            "distanciaPivote1" real,
            "distanciaPivote2" real,
            "distanciaPivote3" real,
            "distanciaPivote4" real,
            "distanciaPivote5" real,
            "distanciaPivote6" real,
            "distanciaPivote7" real,
            "distanciaPivote8" real,
            "distanciaPivote9" real,
            "distanciaPivote10" real,
            PRIMARY KEY(ruta)
        )
    """,
    """
    ALTER TABLE public.imagenes OWNER TO postgres
    """,
    """
    ALTER TABLE public.pivotes OWNER TO postgres
    """,
    """
    ALTER TABLE public."firmasFQA" OWNER TO postgres
    """
    )
    for command in commands:
        cursor.execute(command)
    conn.commit()


#Carga todas las imagenes del dataset en la base de datos, guardando ruta y vector caracteristico
def generarDB(path):
    conn = None
    try:
        conn = conectarAPostgres()
        cursor = conn.cursor()
        crearTablas(conn, cursor)
        listaDirectorio = os.listdir(path)
        for directorio in listaDirectorio:
            subpath = f'{path}/{directorio}'
            listaSubDirectorio = os.listdir(subpath)
            print('En directorio:' + directorio)
            for archivo in listaSubDirectorio:
                if archivo.endswith('.png') or archivo.endswith('.jpg') or archivo.endswith('.jpeg'):
                    rutaImagen = f'{subpath}/{archivo}'
                vec = obtenerVectorImagen(rutaImagen)
                cursor.execute('INSERT INTO imagenes (ruta,vector) VALUES (%s,%s);', [rutaImagen, vec.tolist()])
            conn.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
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
    conn = None
    try:
        conn = conectarAPostgres()
        cursor = conn.cursor()

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
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


#Genera y carga todas las firmas de los elementos a la tabla de firmas
def generarFirmasFQA():
    conn = None
    try:
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
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#Cargado de la base de datos
print('Iniciando...')
print('Cargando imagenes')
generarDB(raiz)
print('Seleccion Incremental')
seleccionIncremental(10, 30, 100)
print('Generando firmas FQA')
generarFirmasFQA()
print('Finalizado.')

