# Proyecto Final GAD

_Este proyecto final consiste en una herramienta que mediante la utilización de un árbol FQA se pueda realizar una búsqueda por similitud de piedras preciosas.

### Comenzando 🚀

_Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

### ¿Cómo funciona la herramienta? 😯

FQA

### Pre-requisitos 📋

_Que cosas se necesitan para hacer correr la herramienta

* [Gemstone Images](https://www.kaggle.com/lsind18/gemstones-images)
* [postgreSQL v12.4](https://www.enterprisedb.com/postgresql-tutorial-resources-training?cid=48)

### Instalación 🔧
_Para poder hacer funcionar el programa, primero tenemos que realizar la conexión a la base de datos correspondiente en donde se van a almacenar las tablas con los pivotes
y vectores correspondientes

_En el archivo correspondiente a: [cargarDB](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/cargarDB.py) _se debe especificar la base de datos a utilizar, el usuario y la contraseña (proyectoGAD, postgres, investigacion en este caso)

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
_Insertamos el dataset nuestro en la ubicación que nosotros queramos, en nuestro caso es "C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images"

_Además, en el archivo:_ [main.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/main.py) _precisamente en la funcion "ObtenerImagen()" también tenemos que cambiar la ruta de initialdir con la ruta correspondiente al dataset de test

```
rutaNueva = filedialog.askopenfilename(initialdir="C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images\test", title="Seleccionar imagen", filetypes=(("JPEG (*.jpg; *.jpeg)", "*.jpg .jpeg"), ("PNG (*.png)", "*.png"), ("All files", "*.*")))
```

_Finalmente, para que funcione la imágen de preview, en el archivo: [metodos.py](https://github.com/LucasMartinPrado/ProyectoFinalGAD/blob/master/metodos.py) _debemos especificar la ruta de una imágen en la función "agregarImagen()", en nuestro caso es
```
rutaImg = 'C:\Users\Fernando\Desktop\ProyectoFinalGAD-master\assets\images\train\Alexandrite\alexandrite_7.jpg'
```

_De esta forma ya tenemos la herramienta lista para correr.

## Construido con 🛠️

* [Python 3.6](https://www.python.org/) - El lenguaje utilizado para desarrollar la herramienta.
* [Python Image Library](https://www.pythonware.com/products/pil/) - Librería que provee al interprete de Python con capacidades de edición de fotos.
* [Psycopg](https://pypi.org/project/psycopg2/) - Adaptador de base de datos PostgreSQL para Python.
* [numpy](https://pypi.org/project/numpy/) - Librería para utilizar estructuras de datos y operaciones basadas en el álgebra lineal.
* [tkinter](https://docs.python.org/3/library/tkinter.html) - Librería para diseño de GUI de Python.


## Autores ✒️

* **Prado, Lucas Martin** - [LucasMartinPrado](https://gitlab.com/LucasMartinPrado)
* **Pereyra Rausch, Fernando Nahuel** - [fernando1544](https://gitlab.com/fernando1544)
