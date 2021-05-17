import tkinter
from tkinter import filedialog
from metodos import *
from PIL import Image, ImageTk



#####Metodos#####

#Selecciona la imagen a buscar
def obtenerImagen():
    global imagenBuscada
    global rutaImagenBuscada
    rutaImagenBuscada = filedialog.askopenfilename(initialdir="C:/GAD/TPFinal/test", title="Seleccionar imagen", filetypes=(("JPEG (*.jpg; *.jpeg)", "*.jpg .jpeg"), ("PNG (*.png)", "*.png"), ("All files", "*.*")))
    image = Image.open(rutaImagenBuscada)
    imagenBuscada = ImageTk.PhotoImage(image.resize((100, 100), Image.ANTIALIAS))
    imagenBuscada_label = tkinter.Label(image=imagenBuscada)
    rutaImagenBuscada_label = tkinter.Label(text=rutaImagenBuscada.split("/")[-1])
    imagenBuscada_label.grid(row=3, column=2)
    rutaImagenBuscada_label.grid(row=4, column=2)

#Muestra una imagen en pantalla a partir de una ruta.
def displayImg(ruta, columna):
    image = Image.open(ruta)
    photo = ImageTk.PhotoImage(image.resize((100,100), Image.ANTIALIAS))
    photos.append(photo)
    name = ruta.split("/")[-1]
    newPhoto_label = tkinter.Label(image=photo)
    newPhoto_label.grid(row=7+2*(columna//5), column=columna%5)
    path_label = tkinter.Label(text=name)
    path_label.grid(row=8+2*(columna//5), column=columna%5)


#Hace la busqueda por similitud y muestra los resultados.
def busquedaSimilitud():
    global rutaImagenBuscada
    ruta = rutaImagenBuscada
    imagen = Image.open(ruta)
    v = obtenerVectorImagen(ruta)
    lista = consultaFQA(v, 3)
    listaSimil = (mostrarPorSimilitud(lista, 10))
    columna = 0
    for imagen in listaSimil:
        displayImg(imagen[0], columna)
        columna += 1



    print(listaSimil)



##Pantallas

#Pantalla principal
root = tkinter.Tk()
root.title('Proyecto Final GAD')
root.geometry("800x600")

#Variables Globales
rutaImagenBuscada = ''
imagenBuscada = 0
photos = [] #Vector de imagenes

#Nombre del Proyecto
label1 = tkinter.Label(root, text="Proyecto Final GAD")
label1.grid(row=0,column=0)
#Boton obtener imagen
buttonMethod = tkinter.Button(root, text="Obtener imagen", padx=10, pady=10, bg="orange", command=obtenerImagen)
buttonMethod.grid(row=1, column=0)
#Preview imagen buscada

#Boton busqueda
buttonMethod = tkinter.Button(root, text="Buscar similares", padx=10, pady=10, bg="orange", command=busquedaSimilitud)
buttonMethod.grid(row=5, column=0)
label2 = tkinter.Label(root, text="Resultados de la busqueda")
label2.grid(row=6, column=0)




root.mainloop()





