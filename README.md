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


### ¿Que caracteristicas de una gema se consideran? 💎
Se consideran principalmente la forma y los colores predominantes para formar el vector característico. 
Para la forma se utiliza la librería img2vec y para los colores utilizamos histogramas de colores.
Los histogramas nos permiten obtener las frecuencias de aparición de colores RGB de una imagen, separados cada uno por canal (rojo, verde, azul) para luego normalizarlos. Al hacer esto, nos habíamos encontrado con la particularidad de que los histogramas también estaban tomando los fondos de las imágenes de las piedras preciosas, por lo que se procedió a crear una función de "masking" que se le aplica a estas imágenes, detectando los bordes correspondientes para luego hacer que se ignore la parte enmascarada de la imágen. En definitiva, se detecta que parte de la imagen es gema y que parte de la imagen es fondo, ignorando esta última.
Para hacer todo esto, utilizamos la librería Skimage. Al detectar los bordes, tuvimos que aplicar un valor "threshold" (de límite) dinámico usando método de Otsu. El valor límite se estableció como dinámico debido a unos factores a tener en cuenta:
- Las gemas también tienen variedad de colores, si se coloca un threshold incorrecto se podría enmascarar partes de la gema.
- Los fondos, por lo general, no son iguales. Hay fondos blancos, negros y hasta incluso grises, por lo que tambien hay que detectar si la gema es mas clara o mas oscura que el fondo para detectar correctamente la parte relevante de la imagen.

De esta forma, siendo dinámico, ya no tendríamos estos problemas. Finalmente obtuvimos resultados muy buenos respecto a la predicción.

### ¿Y que tan bien funciona? 😲

Para medir la eficiencia de la herramienta se utiliza un método que recorre el directorio que contiene las imágenes de prueba y compara los resultados de realizar una consulta a la base de datos con el resultado que esperamos obtener de dicha consulta, siendo el resultado esperado  la misma familia de gemas que la imagen consultada.
Además se miden tres tipos distintos de precisión: los tres primeros resultados, los cinco primeros resultados y los diez primeros resultados. 
Por ejemplo: Si se consulta una imagen de un topacio y el segundo resultado es un topacio, eso cuenta como un acierto entre los tres primeros, los cinco primeros y los diez primeros. No consideramos relevante para esta prueba si hay multiples aciertos dentro de la misma consulta, solo consideramos si se encuentra al menos un resultado o no dentro del rango de cada tipo.
Entonces, el método cuenta la cantidad de veces que se detecta al menos un resultado esperado en esos tipos de precisión y al terminar de recorrer las carpetas devuelve el total acumulado para cada categoría.
Actualmente la carpeta de pruebas cuenta con 363 imágenes y los resultados de las pruebas realizadas fueron 285 aciertos (78,51%) entre los primeros tres, 302 (83,20%) aciertos entre los primeros cinco, y 315 aciertos (86,78%) entre los primeros diez.

### Pre-requisitos 📋

Que cosas se necesitan para hacer correr la herramienta

* [Gemstone Images](https://www.kaggle.com/lsind18/gemstones-images)
* [postgreSQL v12.4](https://www.enterprisedb.com/postgresql-tutorial-resources-training?cid=48)


### Instalación 🔧
Para poder hacer funcionar el programa, primero tenemos que realizar la conexión a la base de datos correspondiente en donde se van a almacenar las tablas con los pivotes
y vectores correspondientes

En el archivo correspondiente a: [cargarDB](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/cargarDB.py) se debe especificar la base de datos a utilizar (crearla en caso de no existir), el usuario y la contraseña (proyectoGAD, postgres, password en este caso)

```
#Conexion a la DB
def conectarAPostgres():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="proyectoGAD",
        user="postgres",
        password="password")
    return conn
```

Insertamos el dataset nuestro en la ubicación que nosotros queramos <ubicación-proyecto> ("C:\Users\...\ProyectoFinalGAD-master\assets\images")

Además, en el archivo: [main.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/main.py) precisamente en la funcion "ObtenerImagen()" también tenemos que cambiar la ruta de "initialdir" con la ruta correspondiente al dataset de test

```
rutaNueva = filedialog.askopenfilename(initialdir="<ubicación-proyecto>", title="Seleccionar imagen", filetypes=(("JPEG (*.jpg; *.jpeg)", "*.jpg .jpeg"), ("PNG (*.png)", "*.png"), ("All files", "*.*")))
```

Finalmente, para que funcione la imágen de preview, en el archivo: [main.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/main.py) debemos especificar la ruta de una imágen en la variable global "rutaImagenBuscada", en nuestro caso es

```
rutaImagenBuscada = 'C:\Users\...\ProyectoFinalGAD-master\assets\images\train\Alexandrite\alexandrite_7.jpg'
```

De esta forma ya tenemos la herramienta lista para correr.

## Construido con 🛠️

* [Python 3.6](https://www.python.org/) - El lenguaje utilizado para desarrollar la herramienta.
* [Python Image Library](https://www.pythonware.com/products/pil/) - Librería que provee al interprete de Python con capacidades de edición de fotos.
* [Psycopg](https://pypi.org/project/psycopg2/) - Adaptador de base de datos PostgreSQL para Python.
* [numpy](https://pypi.org/project/numpy/) - Librería para utilizar estructuras de datos y operaciones basadas en el álgebra lineal.
* [tkinter](https://docs.python.org/3/library/tkinter.html) - Librería para diseño de GUI de Python.
* [img2vec](https://github.com/christiansafka/img2vec) - Libreria para transformar las imagenes en vectores.
* [Skimage](https://scikit-image.org/) - Colección de algoritmos para procesado de imágenes. 
* [matplotlib](https://matplotlib.org/) - Librería para crear visualizaciones estáticas, animadas e interactivas en Python.

## Autores ✒️

* **Prado, Lucas Martin** - [prado.lucasm](https://gitlab.com/prado.lucasm)
* **Pereyra Rausch, Fernando Nahuel** - [fernando1544](https://gitlab.com/fernando1544)
