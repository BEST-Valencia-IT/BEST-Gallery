import sys
import pysftp
import time
import tkinter
from tkinter import messagebox
from tkinter import *
from tkinter.simpledialog import askstring
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QFileDialog, QLabel, QPushButton, QTabWidget, QListWidget,QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage, QIcon
import os
from stat import S_ISDIR, S_ISREG

import datetime
 
 # Esta aplicación está basada en el paquete pyQT5 para poder crear la interfaz y en el paquete pysftp para conectar con el servidor principalmente

 # El funcionamiento será mediante una clase que vaya ejecutando sus métodos. Esta clase debe heredar una clase superior que será la interfaz, que trae todos
 # los elementos de la interfaz al programa con el mismo nombre que tiene en el qt5 con un self. delante indicando que pertenece a esta clase.

class ejemploGUI(QMainWindow):

    def __init__(self,conex):
        super().__init__()
        self.version=3.9
        self.conexion=conex
        uic.loadUi("Menu.ui",self)
        self.setFixedSize(self.size())     
        self.iniciar()   

    def iniciar(self):
        self.b_cambiarnom.setEnabled(False)
        self.cancelar.setEnabled(False)
        self.archivos.clicked.connect(self.browsefiles)
        self.cancelar.clicked.connect(self.cancelar_subida)
        self.try_conexion.clicked.connect(self.probar_conex)
        self.archivo_subir=None
        self.joseluis = QPushButton("PyQt5 button") # Esto es TOTAL y ABSOLUTAMENTE necesario.
        self.listWidget.itemClicked.connect(self.seleccionar)
        self.bdescarga.clicked.connect(self.descargar)
        self.lista_online=list()
        self.directorio_actual='/'
        self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.bdescarga.setEnabled(False)
        self.try_conexion_2.clicked.connect(self.probar_conex)
        self.archivos_dir=[]
        self.carpetas_dir=list()
        self.mostrar_logo_best(self.logo_best)
        self.mostrar_logo_best(self.logo_best2)
        self.babrir_carpeta.clicked.connect(self.abrir_carpeta)
        self.babrir_carpeta.setEnabled(False)
        self.volver_atras.setEnabled(False)
        self.volver_atras.clicked.connect(self.carpeta_anterior)
        self.bnueva_carpeta.clicked.connect(self.crear_carpeta)
        self.b_cambiarnom.clicked.connect(self.renombrar)
        self.b_cambiarnom.setEnabled(False)
        self.brecilaje.clicked.connect(self.mover_reciclaje)
        self.listWidget.itemDoubleClicked.connect(self.seleccionar_carpeta)
        self.lista_filtro.itemDoubleClicked.connect(self.abrir_carpeta_filtro)
        self.lineEdit_filtro.setText("")
        self.lineEdit_filtro.installEventFilter(self)
        self.probarlista()
        self.bnueva_carpeta.setEnabled(True)
        self.b_cambiarnom.setEnabled(False)
        self.archivos.setEnabled(True)
        self.ir_dir_filtro.setEnabled(False)
        self.ir_dir_filtro.clicked.connect(self.abrir_carpeta_filtro)
        self.Buscar_filtro.clicked.connect(self.filtrar)
        self.lista_filtro.itemClicked.connect(self.seleccionar_filtro)
        self.subir_carpetas.clicked.connect(self.browsefolders)
        self.Buscar_filtro.setEnabled(True)
        self.subir_carpetas.setEnabled(True)
        self.ir_dir_filtro.setEnabled(False)
        self.brecilaje.setEnabled(False)

 # Inicar es algo complicado, ya que se deben unir todos los botones a sus respectivas funciones, fijar el estado de los 
 # mismos y darle a las etiquetas strings por defecto Muchas variables se mantienen como atributos de clase por su posible utilidad 
 # en un futuro, pero pueden ser modificados y utilizados como simples parámetros y simplificar el constructor y el programa

 # La carpeta "Reciclaje" es la papelera y adonde se envían los archivos en vez de ser borrados. Se mantiene oculta para el usuario
 # (si les damos la verdadera opción de borrar, luego nos lloran)

 # Está ligeramente (bastante (jesús, es demasiado)) desordenado, pues se ha ido añadiendo todo a lo largo de la escritura del programa. 
 # Si sigue este comentario, es que no se ha arreglado (srry)


 # Esta función será la que permita subir los archivos al servidor. Esta función utiliza self.archivo_subir que es una variable que 
 # tiene los archivos con los que actuar en esta función.
 # Tras recorrer la lista de subidas, las sube sin más y te devuelve a la pantalla principal, donde teóricamente querrás verlo.
 # Debes elegir en la sección descargar el directorio donde quieres subir los archivos.  Es algo un poco ortopédico, pero hasta que 
 # no materialicemos ciertas ideas (o sugerencias) funcionará así.

    def subida(self):
    # se ponen las opciones estas para la conexión
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        self.etiqueta.setText("")   
        try:
                with self.conexion.cd(self.directorio_actual): #con el directorio elegido abierto
                    for i in self.archivo_subir:
                        # self.archivo_subir es una lista de rutas, puede haber una o varias. Recorre y las sube
                        self.conexion.put(i)
                    self.cancelar_subida() # resetea la interfaz
                    self.probarlista() # volvemos a listar el directorio
                    messagebox.showinfo("Subida finalizada", "Archivo(s) subido(s) correctamente") # se informa al usuario
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error","No se ha podido subir la selección al servidor")
            self.recoger_error(f"{e} self.subida  {self.version}")

  # hay que darles un trato especial a las carpetas de cara a subirlas, un porculo interesante.
  # estas dos funciones probablemente se puedan unificar, pero es que ya me da tanta pereza por los rollos de las barras
  # los directorios y las gilipolleces, que si está roto no lo arregles

    def subida_carpeta(self):
        subidas_falladas=list()
        indice=self.archivo_subir.rfind("/") # por alguna razón, al recoger la ruta con el qt5 las recoge con barras
         # y luego hay que trabajar con contrabarras
        nombre_carpeta=self.archivo_subir[indice:] # recoges el nombre de la carpeta
        self.conexion.makedirs(nombre_carpeta) # se crea la carpeta en remoto
        # para poder agregar la (nueva) ruta, necesitas este condicional según sea la root u otra carpeta el destino
        if self.directorio_actual=='/':
                self.directorio_actual+=nombre_carpeta
        else:
                self.directorio_actual+='/'+nombre_carpeta
        try:
            # usamos el os para poder recoger las rutas de los archivos de las carpetas. El walk es recursivo y va entrando en las
            # diferentes carpetas, así que todo bien
            # sí, usé Chatgpt, problem?
            for root, dirs, files in os.walk(self.archivo_subir):
                for dir in dirs:
                    # recoge el nombre de manera algo perezosa pero así tiene que ser 
                    remote_dir = os.path.join(self.directorio_actual, os.path.relpath(os.path.join(root, dir), self.archivo_subir))
                    remote_dir=remote_dir.replace("\\","/") # lo sustituye por si acaso fuera windows (bruh)
                    self.conexion.makedirs(remote_dir) # crea ese directorio si no existe
                
                for file in files:
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(self.directorio_actual, os.path.relpath(local_file, self.archivo_subir))
                    # recogemos la ruta para poder subir los archivos igual que antes de manera ultraperezosa
                    remote_file=remote_file.replace("\\","/")
                    try:
                        self.conexion.put(local_file, remote_file) # lo sube sin más
                    except:
                        subidas_falladas.append(local_file)
            self.carpeta_anterior() # no recuerdo por qué está pero bueno algún sentido tendrá
            self.probarlista()
            # resetea todo 
            messagebox.showinfo("Subida finalizada","La carpeta se ha subido correctamente")
            self.cancelar_subida()
            subidas_falladas=["hola","hola","hola","hola","hola","hola","hola","hola","hola","hola","hola","hola","hola","hola","hola"]
            if len(subidas_falladas)!=0:
                 cadena="\n".join(subidas_falladas)
                 messagebox.showwarning("Fallo",f"No se han podido subir los siguientes elementos:\n {subidas_falladas}")
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error","No se ha podido subir la carpeta al servidor")
            self.recoger_error(f"{e} self.subida  {self.version}")


 # Estas dos funciones permiten reestablecer la conexión. Tanto si se ha inicializado si la misma, se ha perdido durante la ejecución
 # o simplemente ha saltado error y quieres asegurarte de que todo funciona, en descargar y en subir tienes la posibilidad de hacerlo. 
 # Cada función corresponde a una pestaña (¡Ojo! Están al revés, sería tan sencillo como cambiar un número al ligar los botones,
 # pero bueno ahí está)

    def probar_conex(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        try:
                conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
                self.conexion=conexion
                self.iniciar()
                messagebox.showinfo("Finalizado", "Conexión reestablecida")
                # Establece conexión
        except:
            # Si salta error, se avisa al usuario no tiene sentido mandar log al server si no hay conexión
            messagebox.showerror("Error de conexión", "Asegúrate de pagar el wifi antes de volver a intentarlo")

 # Si se anula la subida, se fija lo necesario a False y se anulan la variable a la que estaba ligada (self.archivo_subir) y 
 # a los botones se les devuelve su función de examinar

    def cancelar_subida(self):
        self.cancelar.setEnabled(False)
        self.archivos.setEnabled(True)
        self.subir_carpetas.setEnabled(True)
        self.archivo_subir=None
        # Vale, esto es un coñazo. Para poder desconectar todo, hay que ir probando si tienen conexión a las funciones y reventarlas
        # si es el caso
        try:
            self.archivos.clicked.disconnect(self.browsefiles)
        except:pass
        try:
            self.archivos.clicked.disconnect(self.subida)
        except:pass
        try:
            self.subir_carpetas.clicked.disconnect(self.browsefolders)
        except:pass
        try:
            self.subir_carpetas.clicked.disconnect(self.subida_carpeta)
        except: pass
        # Con todo desconectado, recuperas los botones
        self.archivos.clicked.connect(self.browsefiles)
        self.subir_carpetas.clicked.connect(self.browsefolders)
        self.archivos.setText("Examinar archivo(s)")
        self.subir_carpetas.setText("Examinar carpeta")
        self.prefoto.clear()
        self.etiqueta.setText("")


 # Esta es, básicamente, la función de examinar. Permite al usuario buscar en su SO los archivos que quiere subir, se genera un string
 # como respuesta para una etiqueta y se cambian las etiquetas y botones de manera acorde.
 # Si es posible, mostrará una vista previa del último elemento visualizable de la lista.

    def browsefiles(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, 'Open file') # Buscas el nombre de los archivos
            # fname va a ser una lista con dos elementos. El primero es una lista de las rutas de los archivos, el segundo no sirve
            if fname[0] != '' or len(fname[0]) != 0: # si no está vacía la lista que devuelve, se configuran las etiquetas y botones
                a = self.generar_string(fname[0]) # generamos un string medio bonito en una función que está por el final
                self.etiqueta.setText(f'Archivos y ruta de los archivos:\n\n{a}')
                self.archivo_subir = fname[0]
                self.cancelar.setEnabled(True) # reconfiguramos la ventanita 
                self.archivos.clicked.disconnect(self.browsefiles)
                self.archivos.clicked.connect(self.subida)
                self.archivos.setText("Subir archivo")
                self.subir_carpetas.setEnabled(False)
                self.mostrar_imagen() # y vista previa de la imagen
            else:
                self.etiqueta.setText("No se ha seleccionado ningún archivo.")
        except IndexError:
        # Es el error que salta al cerrar la ventana. Como es lo único que puede ocurrir y está controlado, no lo trataremos como un error.
            self.etiqueta.setText("No se ha seleccionado ningún archivo.")


 # Esta función permite elegir carpetas. Está separada de la otra porque no se puede seleccionar una mezcla de archivos y carpetas.

    def browsefolders(self):
        try:
            fname = QFileDialog.getExistingDirectory(self, 'Open folder') # Recoges el directorio y repites como self.browsefiles()
            if fname != '' or len(fname) != 0:
                self.etiqueta.setText(f'Archivos y ruta de los archivos:\n\n{fname}')
                self.archivo_subir = fname
                self.cancelar.setEnabled(True)
                self.archivos.setEnabled(False)
                self.subir_carpetas.clicked.disconnect(self.browsefolders)
                self.subir_carpetas.clicked.connect(self.subida_carpeta)
                self.subir_carpetas.setText("Subir carpeta")
            else:
                self.etiqueta.setText("No se ha seleccionado ninguna carpeta.")
        except IndexError:
            # Es el error que salta al cerrar la ventana. Como es lo único que puede ocurrir y está controlado,
            # no lo trataremos como un error.
            self.etiqueta.setText("No se ha seleccionado ninguna carpeta.")

 # Esta es de las funciones más importantes. Este método accede a la lista de la pestaña "Descargar" y añade los 
 # elementos que están en el servidor.

    def probarlista(self):
        self.listWidget.clear()
        try:
                
                with self.conexion.cd(self.directorio_actual):
                    print("a")
                    lista=self.conexion.listdir() # Obtenemos lo que hay en el directorio. En definitiva, la salida de los
                    # comandos "ls" o "dir"
                    self.archivos_dir=[]
                    self.carpetas_dir=list() # Con estas listas podremos separar archivos de carpetas, 
                    # poniendo primero las carpetas. Además, no será necesario comprobar qué son a la hora de asignarles la foto
                    for nombre in lista:
                        if nombre!='Reciclaje' or 'Reciclaje' in nombre: # Comprobamos que no es la carpeta de reciclaje
                            # y que no está la misma en su ruta
                            if self.conexion.isdir(nombre)==True: # Dependiendo de si es carpeta o archivo, se lleva a una lista o a otra
                                self.carpetas_dir.append(nombre)
                            else: self.archivos_dir.append(nombre)

                    self.imagenes_lista(self.listWidget)
                    self.brecilaje.setEnabled(False)
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            # También se fijan estos mensajes en las etiquetas para advertir de la gravedad del error.
            self.label_3.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_4.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_5.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            messagebox.showerror("Error", "Ha habido un error mostrando los archivos de esta carpeta")
            self.recoger_error(f"{e} self.probarlista  {self.version}")
        self.b_cambiarnom.setEnabled(False)

    def imagenes_lista(self, objeto):
        try:
            for i in self.carpetas_dir:
                item_carpeta = QListWidgetItem(i)
                item_carpeta.setIcon(QIcon("./Imágenes/carpeta.png"))
                objeto.addItem(item_carpeta)
        except:
            for i in self.carpetas_dir: objeto.addItem(i)

        for i in self.archivos_dir:
                try:
                    item_archivo=QListWidgetItem(i)
                    i=f"    {i}"
                    if i[-4:]==".png" or i[-4:]==".jpg" or i[-5:]==".jpeg":
                        item_archivo.setIcon(QIcon("./Imágenes/Foto_imagen.png"))
                        objeto.addItem(item_archivo)
                    elif i[-4:]==".doc" or i[-5:]==".docx":
                        item_archivo.setIcon(QIcon("./Imágenes/foto_word.png"))
                        objeto.addItem(item_archivo)
                    elif i[-5:]==".pptx":
                        item_archivo.setIcon(QIcon("./Imágenes/Foto_powerpoint.png"))
                        objeto.addItem(item_archivo)                                                
                    elif i[-4:]==".csv":
                        item_archivo.setIcon(QIcon("./Imágenes/Foto_csv.png"))
                        objeto.addItem(item_archivo)  
                    elif i[-4:]==".xls" or i[-5:]==".xlsx":
                        item_archivo.setIcon(QIcon("./Imágenes/Foto_excel.png"))
                        objeto.addItem(item_archivo)                                                  
                    elif i[-4:]==".txt":
                        item_archivo.setIcon(QIcon("./Imágenes/foto_texto.png"))
                        objeto.addItem(item_archivo)                         
                    else:
                        item_archivo.setIcon(QIcon("./Imágenes/Iconoarchivo.png"))
                        objeto.addItem(item_archivo)
                except Exception as e:
                       print(e)
                       objeto.addItem(i)

 # Este método permite obtener el archivo clickado en el listwidget de descargas y lo convierte en variable de clase 
 # para trabajar con él si se quiere descargar o se quiere entrar en esa carpeta.

    def seleccionar(self,lstItem):
        self.label_archivo_elegido.setText(f'Has elegido: {lstItem.text()}')
        self.archivo_descargar=lstItem.text() # se recoge en variable de clase
        # Se cambian los botones pertinentes
        self.bdescarga.setEnabled(True)
        self.b_cambiarnom.setEnabled(True)
        self.brecilaje.setEnabled(True)
        # Si es una carpeta, se permitirá entrar en la misma
        if self.archivo_descargar in self.carpetas_dir:
            self.babrir_carpeta.setEnabled(True)
        else: self.babrir_carpeta.setEnabled(False)


 # Este método permite la descarga de la seleccion. Tras elegir el destino, se comprobará si se descarga un archivo o una carpeta
 # para utilizar un método u otro de la librería y se ajustará la interfaz

    def descargar(self):
        try:
            directorio_destino = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta de destino")
            if directorio_destino:
                if conexion.isdir(self.archivo_descargar):
        # Esto es una pesca un poco complicada para que pueda funcionar en cualquier sistema (bueno no hemos probado mac pero recemos)
        # Recomiendo no tocarlo, este método es un poco delicado y quisquilloso en 
        # cuanto a los SO, mejor dejarla estar (si no está roto no lo arregles)
                    pordescargar=self.directorio_actual+self.archivo_descargar
                    self.conexion.get_r(pordescargar,directorio_destino)
                    self.label_archivo_elegido.setText('')
                    self.bdescarga.setEnabled(False)
                    self.archivo_descargar=None
                    messagebox.showinfo("Finalizado","Carpeta descargada")
                else:
                    # si es archivo la cosa es más tranquilo, no se romperá así como así
                    # miras a ver las rutas para poder elegir
                    with self.conexion.cd(self.directorio_actual):
                        if self.directorio_actual!='/':
                            pordescargar=self.directorio_actual+'/'+self.archivo_descargar
                        else:
                            pordescargar=self.directorio_actual+self.archivo_descargar
                        # arreglas ruta y lo mandas a descargar
                        self.conexion.get(pordescargar,localpath=os.path.join(directorio_destino,self.archivo_descargar))
                        self.label_archivo_elegido.setText('')
                        self.bdescarga.setEnabled(False)
                        self.archivo_descargar=None
                        messagebox.showinfo("Finalizado","Archivo descargado")
        except Exception as e:
               # Si salta error, se avisa al usuario y se manda un log al servidor.
               self.label_archivo_elegido.setText('Ha habido un fallo al descargar. Una posible razón es que exista un archivo con el mismo nombre (y que ya lo hayas descargado).')
               messagebox.showerror("Error", "Ha habido un fallo al descargar")
               self.recoger_error(f"{e} self.descargar  {self.version}")


 # Este método tratará de mostrar la previsualización del archivo que se quiere subir al servidor. Según si es uno o varios, 
 # tratará de visualizar nel último que sea posible (a ver si se pudiera  hacer una buena división de la etiqueta o algo así y
 # se pudieran ver)

    def mostrar_imagen(self):
            # si solo hay una foto pues se intenta visualizar y ya
            if len(self.archivo_subir)==1:
                    imagen_predeterminada = self.archivo_subir[0]
                    image = QImage(imagen_predeterminada)
                    self.prefoto.setPixmap(QPixmap.fromImage(image))
                    self.prefoto.setScaledContents(True)
            else:
                for imagen in self.archivo_subir:
                        imagen_predeterminada = imagen
                        image = QImage(imagen_predeterminada)
                        # como hay varios, se tratará de mostrar el último que sea posible.
                        if image.isNull() is False: # este método comprueba que no sea imposible mostrarla y procede a ello
                            self.prefoto.setPixmap(QPixmap.fromImage(image))
                            self.prefoto.setScaledContents(True)

 # Simplemente muestra el logo de BEST en las dos primeras pestañas. Si no lo encuentra pasa olímpicamente y ya.

    def mostrar_logo_best(self,objeto):
        try:
            imagen_predeterminada = './Imágenes/Logo_apli.png'
            image = QImage(imagen_predeterminada)
            objeto.setPixmap(QPixmap.fromImage(image))
            objeto.setScaledContents(True)
        except: pass

# El método permite desde el listwidget entrar a las diferentes carpetas. Comprobará si está en la raíz o no para añadir los nombres a la ruta de una manera o de otra
# y utilizará probar lista para mostrar el contenido de esa carpeta tras fijarla como directorio actual

    def abrir_carpeta(self):
        # Miras a ver las rutas para echar cuentas
        try:
            if self.directorio_actual=='/':
                self.directorio_actual+=self.archivo_descargar
            else:
                self.directorio_actual+='/'+self.archivo_descargar
            self.archivo_descargar=None
            # llamas a probarlista, listamos el nuevo directorio y se resetea un poco la interfaz
            self.probarlista()
            self.babrir_carpeta.setEnabled(False)
            self.volver_atras.setEnabled(True)
            self.label_archivo_elegido.setText('')
            self.brecilaje.setEnabled(False)
            self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
            self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
            self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error", "No se ha podido abrir esta carpeta")
            self.recoger_error(f"{e} self.abrir_carpeta  {self.version}")

 # Este método cortito descompone una ruta para encontrar el directorio padre

    def dir_padre(self,directorio):
        indice_barra = directorio.rfind("/")
        directorio_padre = directorio[:indice_barra]
        return directorio_padre

 # La función self.carpeta_anterior() permite volver al directorio padre, obtenido con self.dir_padre()

    def carpeta_anterior(self):
        # seguimos con el rollo de las rutas pero de manera algo más compleja
        if self.directorio_actual!='/' and self.dir_padre(self.directorio_actual)!='':
            self.directorio_actual=self.dir_padre(self.directorio_actual)
        else: self.directorio_actual='/'
        if self.directorio_actual=='/':
            self.volver_atras.setEnabled(False)
        # arreglamos la interfaz
        self.label_archivo_elegido.setText('')
        self.probarlista()
        self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")

 # Esta es la función que permite obtener el nombre de la carpeta del listwidget, llamar al servidor para comprobar si es un directorio (comprobación redundante pero por si lo que fuera) y abrir la carpeta

    def seleccionar_carpeta(self,lstItem):
        self.nombre_archivo=lstItem.text()
        with self.conexion.cd(self.directorio_actual):
            if self.conexion.isdir(self.nombre_archivo):
                self.abrir_carpeta()

 # El método pregunta el nombre de la carpeta (si no se escribe nada se entiende que es "Nuva Carpeta"). Se impide que haya dos con el mismo nombre (lo retocaremos para que salga lo de los numeritos)
 # Se ajusta la interfaz y se lista de nuevo el directorio con la carpeta existente

    def crear_carpeta(self):
        nombre_carpeta=askstring(" ","¿Cuál es el nombre de la carpeta?") # Pedimos el nombre de la carpeta
        if nombre_carpeta=="": nombre_carpeta="Nueva Carpeta" # si no hay nombre, se le da nueva carpeta 
        if nombre_carpeta: # si no es false (durante la programación podía ser False, yo qué sé )
            if self.directorio_actual!='/': nueva=self.directorio_actual+'/'+nombre_carpeta
            else: nueva=self.directorio_actual+nombre_carpeta
            try:
                    # qué pereza ya las ruta coño    
                    if self.conexion.isdir(nueva):
                        i=2
                        while(self.conexion.isdir(f"{nueva} ({i})")==True):                            
                            i+=1
                        nueva=f"{nueva} ({i})"                        
                    self.conexion.makedirs(nueva)
                    self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    messagebox.showinfo("Finalizado","Carpeta creada correctamente")
                    self.probarlista()

            except Exception as e:
                # Si salta error, se avisa al usuario y se manda un log al servidor.
                messagebox.showerror("Error", "No se ha podido crear la carpeta")
                self.recoger_error(f"{e} self.crear_carpeta  {self.version}")

 # Permite renombrar una carpeta o archivo y comprueba si está o no en la raíz para crear
 # la ruta de manera adecuada y procede a llamar al servidor para cumplir el objetivo. Se reajusta la interfaz. 
 # No se permiten nombre iguales

 # Es idéntica a poner crear carpeta pero cambiando el makedirs por el rename

    def renombrar(self):
        try:
            nombre_carpeta = askstring('Renombrar', 'Inserta el nuevo nombre')
            if nombre_carpeta is not None and nombre_carpeta!='':
                if self.directorio_actual!='/':
                    nueva=self.directorio_actual+'/'+nombre_carpeta
                    vieja=self.directorio_actual+'/'+self.archivo_descargar
                else:
                    nueva=self.directorio_actual+nombre_carpeta
                    vieja=self.directorio_actual+self.archivo_descargar
                if self.conexion.isdir(nueva)==True:
                    i=2
                    while(self.conexion.isdir(f"{nueva} ({i})")==True):
                        i+=1
                    while(self.conexion.isfile(f"{nueva} ({i})")==True):
                        i+=1
                    nueva=f"{nueva} ({i})"
                    self.conexion.rename(vieja,nueva)
                messagebox.showinfo("Finalizado","Selección renombrada correctamente")
                self.probarlista()
                self.label_archivo_elegido.setText("")

        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showwarning("Error","No se ha podido renombrar")
            self.recoger_error(f"{e} self.renombrar  {self.version}")

 # Permite mover una carpeta o archivo al reciclaje, oculto para el usuario. Pregunta primero si desea borrarle de manera definitiva y se hace los reajustes según es archivo o carpeta
 # para desplazar las selecciones a recicjale.

    def mover_reciclaje(self):
            respuesta=messagebox.askyesno("¡Atención!","¿Seguro que quieres borrar este archivo?") # se pregunta
            if respuesta==True:
                try:
                        if self.directorio_actual!='/':
                            objetivo="Reciclaje/"+self.archivo_descargar
                            actual=self.directorio_actual+'/'+self.archivo_descargar
                        else:
                            objetivo="Reciclaje"+self.directorio_actual+self.archivo_descargar
                            actual=self.directorio_actual+self.archivo_descargar
                        if self.conexion.isdir(objetivo) or self.conexion.isfile(objetivo):
                            i=2
                            while(self.conexion.isdir(f"{objetivo} ({i})")==True):
                                i+=1
                            while(self.conexion.isfile(f"{objetivo} ({i})")==True):
                                i+=1
                            objetivo=f"{objetivo} ({i})"
                        self.conexion.rename(actual,objetivo)
                        self.probarlista()
                except Exception as e:
                    print(e)
                    # Si salta error, se avisa al usuario y se manda un log al servidor.
                    messagebox.showerror("Error","No se ha podido borrar la selección")
                    self.recoger_error(f"{e} self.mover_reciclaje {self.version}")

 # Esta es la función que permite obtener los errores ocurridos en la interfaz. Es posible que aún salten errores controlados

    def recoger_error(self, error):
            current_datetime = datetime.datetime.now()
            date_time_string = current_datetime.strftime('%Y-%m-%d_%H:%M') # Recoge día hora y le pone su nombre para aislar el log
            log_filename = f'registro_errores_{date_time_string}.txt'
            try:
                with conexion.open(f"/Reciclaje/{log_filename}","a") as file:
                    file.write(error) # Se pone en modo añadir para que no se reescriba un error por otro del mismo min

            except: pass # Si no se puede mandar al servidor, F porque no es plan guardarlos en local. 
            # Además, lo normal que si haya conexión y los fallos hayan dado debido a problemas con el servidor y con conexión
    

 # Permite que puedas pulsar Enter en el listwidget de filtrar y funcione. Yo solo cambie el nombre del objeto, ni zorra del como va.

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.lineEdit_filtro:
            if event.key() == QtCore.Qt.Key_Return and self.lineEdit_filtro.hasFocus():
                self.filtrar()
        return super().eventFilter(obj, event)

 # Filtrar permite encontrar las coincidencias que los usuarios buscan en el servidor. Tras elegir un string que buscar mayor que 2, se obtiene todo el árbol del servidor. Como es una lista y no habrá 3 gb,
 # no se hace terrible el coste. Recoge las coincidencias, separándolas en las dos lisas para poder asignar la foto que le toca de la misma manera que en la pestaña de descargar.
 # Por supuesto, se oculta reciclaje

    def filtrar(self):
        nombre_buscar=self.lineEdit_filtro.text()
        self.lista_filtro.clear()
        if nombre_buscar!='' and len(nombre_buscar)>2:
                self.lista_rutas=list()
                try:
                    self.archivos_dir=[]
                    self.carpetas_dir=list()
                    # Necesitamos una función complicada: walktree. Esta función es un coñazo pero devuelve todo el árbol a las listas
                    conexion.walktree('/',fcallback=self.añadir_fwalktree, dcallback=self.añadir_dirwalktree, ucallback=self.nada)
                    # si está la búsqueda en la ruta, se recoge
                    for ruta in self.lista_rutas:
                        indice_barra = ruta.rfind("/")
                        archivo = ruta[indice_barra+1:]
                        if nombre_buscar.upper() in archivo.upper() and 'Reciclaje' not in ruta:
                            if self.conexion.isdir(ruta):
                                self.carpetas_dir.append(ruta)
                            else: 
                                self.archivos_dir.append(ruta)
                    # misma pesca para enseñarlos que en probarlista()
                    self.imagenes_lista(self.lista_filtro)
                                          
                except Exception as e:
                    # Si salta error, se avisa al usuario y se manda un log al servidor.
                    messagebox.showerror("Error", "No se ha podido realizar la búsqueda")
                    self.recoger_error(f"{e} self.filtrar  {self.version}")

    def añadir_fwalktree(self,filename): self.lista_rutas.append(filename)
    def añadir_dirwalktree(self,dirname): self.lista_rutas.append(dirname)
    def nada(self): pass 
    #Funciones necesarias para poder efectuar el conexion.walktree(). La función obliga a rellenar los parámetros, 
    # así que me invento esto. Solo añaden a las listas creadas arriba.


 # el funcionamiento de este método es idéntico al de abrir carpeta normal, pero seleccionando la carpeta del listwidget_filtro 
 # y llevándote a la pestaña de descargas

    def abrir_carpeta_filtro(self):
        destino=self.archivo_filtrar
        try:
            if conexion.isdir(destino)==True:
                self.directorio_actual=destino
                self.probarlista()
            else:
                directorio=self.dir_padre(destino)
                self.directorio_actual=directorio
                self.probarlista()
            self.ir_dir_filtro.setEnabled(False)
            self.volver_atras.setEnabled(True)
            self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
            self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
            self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
            self.lineEdit_filtro.clear()
            self.lista_filtro.clear()
            self.tabWidget.setCurrentIndex(0)
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error","No se ha podido entrar en esa carpeta")
            self.recoger_error(f"{e} self.abrir_carpeta_filtro  {self.version}")

 # Permite tomar la selección del filtro, igual que el anterior

    def seleccionar_filtro(self, item):
         self.archivo_filtrar=item.text()
         self.ir_dir_filtro.setEnabled(True)

 # Este método es un porro que nos colocamos (mentira fui yo solo pero no me quería sentir tan mal vale?) para darle un string
 # a la etiqueta de los archivos que se quieren subir. El string que recibe es la lista de selecciones y cambiará 
 # según si se manda un solo archivo, 3 o más y ajustará las tabulaciones para que se vean los nombres

    def generar_string(self,fname):
        if len(fname)==1:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            return f"{ruta}\t{fname[0][indice_barra+1:]}"
        elif len(fname)>=3:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            for i in range(0,3):
                    ruta+=f"\t\t{fname[i][indice_barra+1:]}"
            ruta+="\t\t..."
        else:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            for i in fname:
                ruta+=f"\t\t{i[indice_barra+1:]}"
        return ruta

# Inicias de una puta vez y de verdad el programa, si falla se inicia sin conexión y si no funciona normal hasta que le des a la cruz

if __name__=='__main__':
    try:
        server_address = 'home500757070.1and1-data.host'
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
        app=QApplication(sys.argv)
        GUI= ejemploGUI(conexion)
        GUI.show()
        sys.exit(app.exec_())
    except Exception as e:
        messagebox.showerror("Error de conexión", "No se ha podido establecer conexión. Paga el wifi")
            
