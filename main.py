import tkinter
from tkinter import filedialog
from metodos import *
from PIL import Image, ImageTk

#Variables Globales
rutaImagenBuscada = 'C:/GAD/TPFinal/train/Alexandrite/alexandrite_7.jpg' #Cargamos esta imagen como preview
imagenPreview = Image.open(rutaImagenBuscada) #Abrimos la imagen preview
photos = [] #Vector de imagenes
cantidadAMostrar = 10 #Mostramos 10 valores por defecto
radioBusqueda = 20    #Usamos un radio de 20 como valor por defecto

#####Metodos#####

#Selecciona la imagen a buscar
def obtenerImagen():
    global imagenBuscada
    global rutaImagenBuscada
    global rutaImagenBuscada_label

    rutaNueva = filedialog.askopenfilename(initialdir="C:/GAD/TPFinal/test", title="Seleccionar imagen", filetypes=(("JPEG (*.jpg; *.jpeg)", "*.jpg .jpeg"), ("PNG (*.png)", "*.png"), ("All files", "*.*")))
    if rutaNueva != '':
        rutaImagenBuscada = rutaNueva
    image = Image.open(rutaImagenBuscada)
    imagenBuscada = ImageTk.PhotoImage(image.resize((100, 100), Image.ANTIALIAS))
    rutaImagenBuscada_label.grid_forget()
    imagenBuscada_label = tkinter.Label(frameBusqueda, image=imagenBuscada)
    rutaImagenBuscada_label = tkinter.Label(frameBusqueda, text=rutaImagenBuscada.split("/")[-1])
    imagenBuscada_label.grid(row=0, column=0)
    rutaImagenBuscada_label.grid(row=1, column=0)

#Muestra una imagen en pantalla a partir de una ruta.
def displayImg(ruta, distancia, columna):
    image = Image.open(ruta)
    photo = ImageTk.PhotoImage(image.resize((100, 100), Image.ANTIALIAS))
    photos.append(photo)
    name = ruta.split("/")[-1]
    newPhoto_label = tkinter.Label(frameResultados, image=photo)
    newPhoto_label.grid(row=3*(columna//5), column=columna%5)
    path_label = tkinter.Label(frameResultados, text=name)
    path_label.grid(row=1+3*(columna//5), column=columna%5)
    distancia_label = tkinter.Label(frameResultados, text='Distancia: ' + str(np.round(distancia, 4)))
    distancia_label.grid(row=2+3*(columna//5), column=columna%5)


#Hace la busqueda por similitud y muestra los resultados.
def busquedaSimilitud():
    global rutaImagenBuscada
    global canvasResultados
    global frameResultados
    global cantidadAMostrar
    global radioBusqueda

    #Actualizamos el valor de radioBusqueda
    if int(entryCantidad.get()) <= 0:
        radioBusqueda = 0
    else:
        radioBusqueda = int(entryRadio.get())

    #Actualizamos el valor de cantidadAMostrar
    if int(entryCantidad.get()) <= 0:
       cantidadAMostrar = 5
    else:
       cantidadAMostrar = int(entryCantidad.get())

    #Actualizamos la pantalla
    frameResultados.destroy()
    frameResultados = tkinter.LabelFrame(canvasResultados)
    canvasResultados.create_window((0, 0), window=frameResultados, anchor=tkinter.NW)

    #Realizamos la busqueda
    ruta = rutaImagenBuscada
    v = obtenerVectorImagen(ruta)
    lista = consultaFQA(v, radioBusqueda)
    listaSimil = (mostrarPorSimilitud(lista, cantidadAMostrar))
    columna = 0
    for imagen in listaSimil:
        displayImg(imagen[0], imagen[1], columna)
        columna += 1

    #Actualizamos el canvas para que pueda usarse la scrollbar
    frameResultados.update_idletasks()
    canvasResultados.configure(scrollregion=canvasResultados.bbox(tkinter.ALL))
    print(listaSimil) #Muestra por consola los resultados con ruta y distancia


###################
#Pantallas

#Pantalla principal
root = tkinter.Tk()
root.title('Proyecto Final GAD')
root.geometry("800x600")
root.resizable(False, False)
bg = ImageTk.PhotoImage(file="assets/background.jpg")
bg_label = tkinter.Label(root, image=bg)
bg_label.place(x=0, y=0)


#Frames
#Frame de Imagen de Busqueda
frameBusqueda = tkinter.LabelFrame(root, text= "Imagen a buscar", padx=5, pady=5)
frameBusqueda.place(x=50, y=50)
#Generamos la vista previa
imagenBuscada = ImageTk.PhotoImage(imagenPreview.resize((100, 100), Image.ANTIALIAS))
imagenBuscada_label = tkinter.Label(frameBusqueda, image=imagenBuscada)
rutaImagenBuscada_label = tkinter.Label(frameBusqueda, text=rutaImagenBuscada.split("/")[-1])
rutaImagenBuscada_label.grid(row=1, column=0)


#Frame de resultados de busqueda
#Frame contenedor
frameBuscados = tkinter.LabelFrame(root, text= "Resultados de la busqueda", padx=5, pady=5)
frameBuscados.place(x=50, y=250)
#Canvas
canvasResultados = tkinter.Canvas(frameBuscados, width=650)
canvasResultados.grid(row=0, column=0)
#Scrollbar
scrollbarResultados = tkinter.Scrollbar(frameBuscados, orient=tkinter.VERTICAL, command=canvasResultados.yview)
scrollbarResultados.grid(row=0, column=1, sticky=tkinter.NS)
canvasResultados.configure(yscrollcommand=scrollbarResultados.set)
#Frame con los resultados
frameResultados = tkinter.LabelFrame(canvasResultados)
#Ventana
canvasResultados.create_window((0, 0), window=frameResultados, anchor=tkinter.NW)
frameResultados.update_idletasks()
canvasResultados.configure(scrollregion=canvasResultados.bbox(tkinter.ALL))


#Boton obtener imagen
buttonMethod = tkinter.Button(root, text="Obtener imagen", padx=10, pady=10, bg="orange", command=obtenerImagen)
buttonMethod.place(x=200, y=100)
#Preview imagen buscada
imagenBuscada_label.grid(row=0, column=0)

#Boton busqueda
buttonMethod = tkinter.Button(root, text="Buscar similares", padx=10, pady=10, bg="orange", command=busquedaSimilitud)
buttonMethod.place(x=350, y=100)


#Input radio de busqueda
entryFrameR = tkinter.LabelFrame(root, text='Radio de busqueda', padx=5, pady=5)
entryFrameR.place(x=190, y=150)
entryRadio = tkinter.Entry(entryFrameR, width=20, borderwidth=1)
entryRadio.pack()
entryRadio.insert(0, radioBusqueda)

#Input cantidad a mostrar
entryFrameC = tkinter.LabelFrame(root, text='Cantidad a mostrar', padx=5, pady=5)
entryFrameC.place(x=340, y=150)
entryCantidad = tkinter.Entry(entryFrameC, width=20, borderwidth=1)
entryCantidad.pack()
entryCantidad.insert(0, cantidadAMostrar)





root.mainloop()





