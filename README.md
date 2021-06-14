# Proyecto Final GAD

Este proyecto final consiste en una herramienta que mediante la utilización de un árbol FQA se pueda realizar una búsqueda por similitud de piedras preciosas.

### Comenzando 🚀

Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

### ¿Cómo funciona la herramienta? 😯

En este proyecto, utilizamos una estructura de datos llamada Fixed Queries Array (FQA) para realizar la búsqueda en espacios métricos. En este se guarda para cada elemento de la base de datos, una lista con las distancias a los _k_ pivotes, considerándose esta lista como una secuencia de _k_ enteros llamada firma; los elementos se ordenan primero por su distancia al primer pivote, y los que tengan la misma distancia al primer pivote, se ordenan por su distancia al segundo pivote, y así sucesivamente. El FQA forma parte de la familia de algoritmos basados en pivotes para  las funciones de distancia discretas. 

Primero se cargan todas las imágenes del dataset en la base de datos, se van guardando sus respectivas rutas y vector característico. Luego se procede a hacer la selección incremental para _k_ pivotes, con _a_ pares a comparar y _n_ pivotes candidatos para cada iteracion; este método consiste en tomar una muestra de _n_ elementos de la base de datos y seleccionar como primer pivote p<sub>1</sub> a aquel elemento que tenga el máximo valor para µ<sub>D</sub>, siendo µ<sub>D</sub> la media de las distancias maximas. El segundo pivote p<sub>2</sub> se elige de otra muestra de _n_ elementos de forma tal que {p<sub>1</sub>, p<sub>2</sub>} tenga el máximo valor para µ<sub>D</sub>. Este proceso se repite hasta terminar de elegir los _k_ pivotes necesitados.
Un buen grupo de pivotes tiene dos características básicas:
En primer lugar, los pivotes están alejados unos de otros, es decir, la distancia media entre pivotes es mayor que la distancia media entre elementos tomados al azar del espacio métrico. En segundo lugar, los pivotes están alejados del resto de los elementos del espacio métrico.

De esta forma, queda conformado el conjunto de pivotes {p<sub>1</sub>, p<sub>2</sub>, ..., p<sub>k</sub>} utilizados para las firmas de cada elemento.
Esto nos permite filtrar, mediante la desigualdad triangular, la firma y un radio arbitrario, objetos de la base datos sin tener que medir su distancia con la query q, descartandose todos aquellos elementos cuya distancia a algun pivote cualquiera sea mayor que el radio elegido.
Luego, con los no descartados, se forma una lista de candidatos que se comparan directamente con la query q para verificar que el elemento este a una distancia menor que el radio de consulta.  Esto significa que la cantidad total de cálculos de la función de distancia d es determinada por la cantidad de pivotes _k_ y la cardinalidad de la lista de candidatos.

Entonces, cada vez que se realiza una consulta, utilizamos la tabla FQA, un vector de entrada y el radio, se obtiene el vector de firmas de la imagen de entrada, luego se filtran los elementos que no se encuentran en el radio de búsqueda y obtenemos aquellos vectores que hayan pasado el filtro, por ultimo comparamos estos vectores con el de entrada para verificar si está dentro del radio, mostrando por pantalla las imágenes gracias a las rutas incluídas en el resultado.

### Pre-requisitos 📋

Que cosas se necesitan para hacer correr la herramienta

* [Gemstone Images](https://www.kaggle.com/lsind18/gemstones-images)
* [postgreSQL v12.4](https://www.enterprisedb.com/postgresql-tutorial-resources-training?cid=48)
* [img2vec](https://github.com/christiansafka/img2vec)

### Instalación 🔧
Para poder hacer funcionar el programa, primero tenemos que realizar la conexión a la base de datos correspondiente en donde se van a almacenar las tablas con los pivotes
y vectores correspondientes

En el archivo correspondiente a: [cargarDB](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/cargarDB.py) se debe especificar la base de datos a utilizar, el usuario y la contraseña (proyectoGAD, postgres, investigacion en este caso)

```
#Conexion a la DB
def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="proyectoGAD",
        user="postgres",
        password="investigacion")
    return conn
```

Insertamos el dataset nuestro en la ubicación que nosotros queramos, en nuestro caso es "C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images"

Además, en el archivo: [main.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/main.py) precisamente en la funcion "ObtenerImagen()" también tenemos que cambiar la ruta de "initialdir" con la ruta correspondiente al dataset de test

```
rutaNueva = filedialog.askopenfilename(initialdir="C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images\test", title="Seleccionar imagen", filetypes=(("JPEG (*.jpg; *.jpeg)", "*.jpg .jpeg"), ("PNG (*.png)", "*.png"), ("All files", "*.*")))
```

Finalmente, para que funcione la imágen de preview, en el archivo: [metodos.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/metodos.py) debemos especificar la ruta de una imágen en la función "agregarImagen()", en nuestro caso es

```
rutaImg = 'C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images\train\Alexandrite\alexandrite_7.jpg'
```

De esta forma ya tenemos la herramienta lista para correr.

## Construido con 🛠️

* [Python 3.6](https://www.python.org/) - El lenguaje utilizado para desarrollar la herramienta.
* [Python Image Library](https://www.pythonware.com/products/pil/) - Librería que provee al interprete de Python con capacidades de edición de fotos.
* [Psycopg](https://pypi.org/project/psycopg2/) - Adaptador de base de datos PostgreSQL para Python.
* [numpy](https://pypi.org/project/numpy/) - Librería para utilizar estructuras de datos y operaciones basadas en el álgebra lineal.
* [tkinter](https://docs.python.org/3/library/tkinter.html) - Librería para diseño de GUI de Python.


## Autores ✒️

* **Prado, Lucas Martin** - [prado.lucasm](https://gitlab.com/prado.lucasm)
* **Pereyra Rausch, Fernando Nahuel** - [fernando1544](https://gitlab.com/fernando1544)
