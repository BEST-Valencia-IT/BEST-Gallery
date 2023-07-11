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

    def __init__(self,conex=None):
        super().__init__()
        self.version=3.2
        self.conexion=conex
        uic.loadUi("Menu.ui",self)
        self.setFixedSize(self.size())

 # Este constructor está pensado para que reciba la conexión del servidor como un parámetro. Si este no estuviera, la aplicación puede iniciarse igualmente, pero su inicio por defecto
 # será vacío, de ahí que todo esté "seteado" a False.

        if self.conexion!=None:
            self.iniciar()
        else:
            self.volver_atras.setEnabled(False)
            self.bnueva_carpeta.setEnabled(False)
            self.b_cambiarnom.setEnabled(False)
            self.brecilaje.setEnabled(False)
            self.babrir_carpeta.setEnabled(False)
            self.bdescarga.setEnabled(False)
            self.cancelar.setEnabled(False)
            self.archivos.setEnabled(False)
            self.try_conexion.clicked.connect(self.probar_conex)
            self.try_conexion_2.clicked.connect(self.probar_conex2)

# Sin embargo, si recibe una conexión funcional, se activará inicar, que inicializa toda la aplicación, siendo el verdadero constructor aunque se aparte a una función.

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
            self.try_conexion_2.clicked.connect(self.probar_conex2)
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

 # Inicar es algo complicado, ya que se deben unir todos los botones a sus respectivas funciones, fijar el estado de los mismos y darle a las etiquetas strings por defecto
 # Muchas variables se mantienen como atributos de clase por su posible utilidad en un futuro, pero pueden ser modificados y utilizados como simples parámetros y simplificar el constructor y el programa
 # La carpeta "Reciclaje" es la papelera y adonde se envían los archivos para ser borrados. Se mantiene oculta para el usuario.

 # Está ligeramente (bastante (jesús es demasiado)) desordenado, pues se ha ido añadiendo todo a lo largo de la escritura del programa. Si sigue este comentario, es que no se ha arreglado (srry)


 # Esta función será la que permita subir los archivos al servidor. Esta función utiliza self.archivo_subir que es una variable que tiene los archivos con los que actuar en esta función.
 # Tras recorrer la lista de subidas, las sube sin más y te devuelve a la pantalla principal, donde teóricamente querrás verlo.
 # Debes elegir en la sección descargar el directorio donde quieres subir los archivos. Es algo un poco ortopédico, pero hasta que no materialicemos ciertas ideas (o sugerencias) se funcionará así.

    def subida(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        self.etiqueta.setText("")
        try:
                with self.conexion.cd(self.directorio_actual):
                    for i in self.archivo_subir:
                        self.conexion.put(i)
                    self.cancelar_subida()
                    self.probarlista()
                    messagebox.showinfo("Subida finalizada", "Archivo(s) subido(s) correctamente")
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error","No se ha podido subir la selección al servidor")
            self.recoger_error(f"{e} self.subida  {self.version}")

    def subida_carpeta(self):
        indice=self.archivo_subir.rfind("/")
        nombre_carpeta=self.archivo_subir[indice:]
        self.conexion.makedirs(nombre_carpeta)
        if self.directorio_actual=='/':
                self.directorio_actual+=nombre_carpeta
        else:
                self.directorio_actual+='/'+nombre_carpeta
        try:
            for root, dirs, files in os.walk(self.archivo_subir):
                # Crear las carpetas remotas si no existen
                for dir in dirs:
                    remote_dir = os.path.join(self.directorio_actual, os.path.relpath(os.path.join(root, dir), self.archivo_subir))
                    remote_dir=remote_dir.replace("\\","/")
                    self.conexion.makedirs(remote_dir)

                # Subir los archivos al directorio remoto
                for file in files:
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(self.directorio_actual, os.path.relpath(local_file, self.archivo_subir))
                    remote_file=remote_file.replace("\\","/")
                    self.conexion.put(local_file, remote_file)
            self.carpeta_anterior()
            self.probarlista()
            messagebox.showinfo("Subida finalizada","La carpeta se ha subido correctamente")
            self.cancelar_subida()
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error","No se ha podido subir la carpeta al servidor")
            self.recoger_error(f"{e} self.subida  {self.version}")
 # Estas dos funciones permiten reestablecer la conexión. Tanto si se ha inicializado si la misma, se ha perdido durante la ejecución o simplemente ha saltado error y quieres asegurarte de que todo funciona,
 # en descargar y en subir tienes la posibilidad de hacerlo. Cada función corresponde a una pestaña (¡Ojo! Están al revés, sería tan sencillo como cambiar un número al ligar los botones pero bueno ahi está)

    def probar_conex(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        try:
                conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
                self.conexion=conexion
                messagebox.showinfo("Finalizado", "Conexión reestablecida")
                self.iniciar()
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error de conexión", "Asegúrate de pagar el wifi antes de volver a intentarlo")
            self.recoger_error(f"{e} self.probarconex  {self.version}")

    def probar_conex2(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        try:
                conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
                self.conexion=conexion
                messagebox.showinfo("Finalizado", "Conexión reestablecida")
                self.iniciar()
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error de conexión", "Asegúrate de pagar el wifi antes de volver a intentarlo")
            self.recoger_error(f"{e} self.probarconex2  {self.version}")

 # Si se anula la subida, se fija lo necesario a False y se anulan la variable a la que estaba ligada (self.archivo_subir) y al botón de la derecha se le devuelve la función de "examinar"

    def cancelar_subida(self):
        self.cancelar.setEnabled(False)
        self.archivos.setEnabled(True)
        self.subir_carpetas.setEnabled(True)
        self.archivo_subir=None
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
        self.archivos.clicked.connect(self.browsefiles)
        self.subir_carpetas.clicked.connect(self.browsefolders)
        self.archivos.setText("Examinar archivo(s)")
        self.subir_carpetas.setText("Examinar carpeta")
        self.prefoto.clear()
        self.etiqueta.setText("")


 # Esta es, básicamente, la función de examinar. Permite al usuario buscar en su SO los archivos que quiere subir, se genera un string como respuesta para una etiqueta y se cambian las etiquetas y botones de manera acorde.
 # Si es posible, mostrará una vista previa del último elemento visualizable de la lista.

    def browsefiles(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, 'Open file')
            if fname[0] != '' or len(fname[0]) != 0:
                a = self.generar_string(fname[0])
                self.etiqueta.setText(f'Archivos y ruta de los archivos:\n\n{a}')
                self.archivo_subir = fname[0]
                self.cancelar.setEnabled(True)
                self.archivos.clicked.disconnect(self.browsefiles)
                self.archivos.clicked.connect(self.subida)
                self.archivos.setText("Subir archivo")
                self.subir_carpetas.setEnabled(False)
                self.mostrar_imagen()
            else:
                self.etiqueta.setText("No se ha seleccionado ningún archivo.")
        except IndexError:
            # Es el error que salta al cerrar la ventana. Como es lo único que puede ocurrir y está controlado, no lo trataremos como un error.
            self.etiqueta.setText("No se ha seleccionado ningún archivo.")

    def  browsefolders(self):
        try:
            fname = QFileDialog.getExistingDirectory(self, 'Open folder')
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
            # Es el error que salta al cerrar la ventana. Como es lo único que puede ocurrir y está controlado, no lo trataremos como un error.
            self.etiqueta.setText("No se ha seleccionado ninguna carpeta.")
 # Esra es de las funciones más importantes. Este método accede a la lista de la pestaña "Descargar" y añade los elementos que están en el servidor.

    def probarlista(self):
        self.listWidget.clear()
        try:
                with self.conexion.cd(self.directorio_actual):
                    lista=self.conexion.listdir() # Obtenemos lo que hay en el directorio. En definitiva, la salida de los comandos "ls" o "dir"
                    self.archivos_dir=[]
                    self.carpetas_dir=list() # Con estas listas podremos separar archivos de carpetas,poniendo primero las carpetas. Además, no será necesario comprobar qué son a la hora de asignarles la foto
                    for nombre in lista:
                        if nombre!='Reciclaje':
                            if self.conexion.isdir(nombre)==True:
                                self.carpetas_dir.append(nombre)
                            else: self.archivos_dir.append(nombre)

                    # Una vez recogidos, se les asigna la foto, si es posible (si no se encontrara la foto que trae la aplicación, entonces no se mostraría)
                    try:
                        for i in self.carpetas_dir:
                            item_carpeta = QListWidgetItem(i)
                            item_carpeta.setIcon(QIcon("carpeta.png"))
                            self.listWidget.addItem(item_carpeta)
                    except:
                        for i in self.carpetas_dir: self.listWidget.addItem(i)

                    try:
                        for i in self.archivos_dir:
                            item_archivo=QListWidgetItem(i)
                            item_archivo.setIcon(QIcon("Iconoarchivo.png"))
                            self.listWidget.addItem(item_archivo)
                    except:
                        for i in self.archivos_dir: self.listWidget.addItem(i)
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            # También se fijan estos mensajes en las etiquetas para advertir de la gravedad del error.
            self.label_3.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_4.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_5.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            messagebox.showerror("Error", "Ha habido un error mostrando los archivos de esta carpeta")
            self.recoger_error(f"{e} self.probarlista  {self.version}")
        self.b_cambiarnom.setEnabled(False)

 # Este método permite obtener el archivo clickado en el listwidget de descargas y lo convierte en variable de clase para trabajar con ´él si se quiere descargar o se quiere entrar en esa carpeta.

    def seleccionar(self,lstItem):
        self.label_archivo_elegido.setText(f'Has elegido: {lstItem.text()}')
        self.archivo_descargar=lstItem.text()
        self.bdescarga.setEnabled(True)
        self.b_cambiarnom.setEnabled(True)
        if self.archivo_descargar in self.carpetas_dir:
            self.babrir_carpeta.setEnabled(True)
        else: self.babrir_carpeta.setEnabled(False)


 # Este método permite la descarga de la seleccion. Tras elegir el destino, se comprobará si se descarga un archivo o una carpeta para utilizar un método u otro de la librería y se ajustará la interfaz

    def descargar(self):
        try:
            directorio_destino = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta de destino")
            if directorio_destino:
                if conexion.isdir(self.archivo_descargar):
                    # Esto es una pesca un poco complicada para que pueda funcionar en cualquier sistema (bueno no hemos probado mac pero recemos)
                    # Recomiendo no tocarlo, aunque ruta local no sirva para nada, este método es un poco delicado y quisquilloso en cuanto a los SO, mejor dejarla estar (si no está roto no lo arregles)
                    pordescargar=self.directorio_actual+self.archivo_descargar
                    ruta_local= os.path.join(directorio_destino,self.archivo_descargar)
                    ruta_local=ruta_local.replace("/","\\")
                    self.conexion.get_r(pordescargar,directorio_destino)
                    self.label_archivo_elegido.setText('')
                    self.bdescarga.setEnabled(False)
                    self.archivo_descargar=None
                    messagebox.showinfo("Finalizado","Carpeta descargada")
                else:
                    with self.conexion.cd(self.directorio_actual):
                        if self.directorio_actual!='/':
                            pordescargar=self.directorio_actual+'/'+self.archivo_descargar
                        else:
                            pordescargar=self.directorio_actual+self.archivo_descargar
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

 # Este método tratará de mostrar la previsualización del archivo que se quiere subir al servidor. Según si es uno o varios, tratará de visualizarlo y ya está
 # o tratará de visualizar el último que sea posible (a ver si se pudiera hacer una buena división de la etiqueta o algo así y se pudieran ver)

    def mostrar_imagen(self):
            if len(self.archivo_subir)==1:
                    imagen_predeterminada = self.archivo_subir[0]
                    image = QImage(imagen_predeterminada)
                    self.prefoto.setPixmap(QPixmap.fromImage(image))
                    self.prefoto.setScaledContents(True)
            else:
                for imagen in self.archivo_subir:
                        imagen_predeterminada = imagen
                        image = QImage(imagen_predeterminada)
                        if image.isNull() is False:
                            self.prefoto.setPixmap(QPixmap.fromImage(image))
                            self.prefoto.setScaledContents(True)

 # Simplemente muestra el logo de BEST en las dos primeras pestañas. Si no lo encuentra pasa olímpicamente y ya.

    def mostrar_logo_best(self,objeto):
        try:
            imagen_predeterminada = 'Logo_apli.png'
            image = QImage(imagen_predeterminada)
            objeto.setPixmap(QPixmap.fromImage(image))
            objeto.setScaledContents(True)
        except: pass

# El método permite desde el listwidget entrar a las diferentes carpetas. Comprobará si está en la raíz o no para añadir los nombres a la ruta de una manera o de otra
# y utilizará probar lista para mostrar el contenido de esa carpeta tras fijarla como directorio actual

    def abrir_carpeta(self):
        try:
            if self.directorio_actual=='/':
                self.directorio_actual+=self.archivo_descargar
            else:
                self.directorio_actual+='/'+self.archivo_descargar
            self.archivo_descargar=None
            self.probarlista()
            self.babrir_carpeta.setEnabled(False)
            self.volver_atras.setEnabled(True)
            self.label_archivo_elegido.setText('')
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
        if self.directorio_actual!='/' and self.dir_padre(self.directorio_actual)!='':
            self.directorio_actual=self.dir_padre(self.directorio_actual)
        else: self.directorio_actual='/'
        if self.directorio_actual=='/':
            self.volver_atras.setEnabled(False)
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
        nombre_carpeta=askstring(" ","¿Cuál es el nombre de la carpeta?")
        if not nombre_carpeta: nombre_carpeta="Nueva Carpeta"
        try:
                if self.directorio_actual!='/': nueva=self.directorio_actual+'/'+nombre_carpeta
                else: nueva=self.directorio_actual+nombre_carpeta
                if(self.conexion.isdir(nueva)==True):
                    messagebox.showwarning("Error", "Nombre de la carpeta ya en uso aquí")
                else:
                    self.conexion.makedirs(nueva)
                    self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    messagebox.showinfo("Finalizado","Carpeta creada correctamente")
                    self.probarlista()
                    self.volver_atras.setEnabled(True)
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showerror("Error", "No se ha podido crear la carpeta")
            self.recoger_error(f"{e} self.crear_carpeta  {self.version}")

 # Permite renombrar una carpeta o archivo y comprueba si está o no en la raíz para crear
 # la ruta de manera adecuada y procede a llamar al servidor para cumplir el objetivo. Se reajusta la interfaz. No se permiten nombre iguales

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
                self.conexion.rename(vieja,nueva)
                messagebox.showinfo("Finalizado","Carpeta renombrada correctamente")
                self.probarlista()
                self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        except OSError as e: messagebox.showwarning("Error","Nombre de la carpeta ya en uso en esta") # Se aisla para no confundirse con un error real
        except Exception as e:
            # Si salta error, se avisa al usuario y se manda un log al servidor.
            messagebox.showwarning("Error","No se ha podido renombrar")
            self.recoger_error(f"{e} self.renombrar  {self.version}")

 # Permite mover una carpeta o archivo al reciclaje, oculto para el usuario. Pregunta primero si desea borrarle de manera definitiva y se hace los reajustes según es archivo o carpeta
 # para desplazar las selecciones a recicjale.

    def mover_reciclaje(self):
        respuesta=messagebox.askyesno("¡Atención!","¿Seguro que quieres borrar este archivo?")
        if respuesta:
            try:
                    if self.directorio_actual!='/':
                        objetivo="Reciclaje/"+self.archivo_descargar
                        actual=self.directorio_actual+'/'+self.archivo_descargar
                    else:
                        objetivo="Reciclaje"+self.directorio_actual+self.archivo_descargar
                        actual=self.directorio_actual+self.archivo_descargar

                    while(self.conexion.isdir(objetivo)==True):
                        self.archivo_descargar='Copia_'+self.archivo_descargar
                        objetivo="Reciclaje"+'/'+self.archivo_descargar

                    while(self.conexion.isfile(objetivo)==True):
                        self.archivo_descargar='Copia_'+self.archivo_descargar
                        objetivo="Reciclaje"+'/'+self.archivo_descargar

                    self.conexion.rename(actual,objetivo)
                    self.probarlista()
            except Exception as e:
                # Si salta error, se avisa al usuario y se manda un log al servidor.
                messagebox.showerror("Error","No se ha podido borrar la selección")
                self.recoger_error(f"{e} self.mover_reciclaje {self.version}")

 # Esta es la función que permite obtener los errores ocurridos en la interfaz. Es posible que aún salten errores controlados

    def recoger_error(self, error):
            current_datetime = datetime.datetime.now()
            date_time_string = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
            log_filename = f'registro_errores_{date_time_string}.txt'
            try:
                with conexion.open(f"/Reciclaje/{log_filename}","a") as file:
                    file.write(error)
            except: pass # Si no se puede mandar al servidor, F porque no es plan guardarlos en local. Además, lo normal que si haya conexión y los fallos hayan dado debido a problemas con el servidor y con conexión
    

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
                    conexion.walktree('/',fcallback=self.añadir_fwalktree, dcallback=self.añadir_dirwalktree, ucallback=self.nada)
                    for ruta in self.lista_rutas:
                        indice_barra = ruta.rfind("/")
                        archivo = ruta[indice_barra+1:]
                        if nombre_buscar.upper() in archivo.upper() and 'Reciclaje' not in ruta:
                            if self.conexion.isdir(ruta):
                                self.carpetas_dir.append(ruta)
                            else: 
                                self.archivos_dir.append(ruta)

                    try:
                        for i in self.carpetas_dir:
                            item_carpeta = QListWidgetItem(i)
                            item_carpeta.setIcon(QIcon("carpeta.png"))
                            self.lista_filtro.addItem(item_carpeta)
                    except:
                        for i in self.carpetas_dir: self.lista_filtro.addItem(i)
                    try:
                        for i in self.archivos_dir:
                            item_archivo=QListWidgetItem(i)
                            item_archivo.setIcon(QIcon("Iconoarchivo.png"))
                            self.lista_filtro.addItem(item_archivo)
                    except:
                        for i in self.archivos_dir: self.lista_filtro.addItem(i)
                    if len(self.lista_filtro)!=0:
                         messagebox.showinfo("Búsqueda finalizada",f"Se ha(n) encontrado {len(self.lista_filtro)} coincidencia(s)")
                    else:
                         messagebox.showwarning("Búsqueda finalizada","No se han encontrado coincidencias")
                         self.ir_dir_filtro.setEnabled(False)
                         
                except Exception as e:
                    # Si salta error, se avisa al usuario y se manda un log al servidor.
                    messagebox.showerror("Error", "No se ha podido realizar la búsqueda")
                    self.recoger_error(f"{e} self.filtrar  {self.version}")

    def añadir_fwalktree(self,filename): self.lista_rutas.append(filename)
    def añadir_dirwalktree(self,dirname): self.lista_rutas.append(dirname)
    def nada(self): pass 
    #Funciones necesarias para poder efectuar el conexion.walktree(). La función obliga a rellenar los parámetros, así que me invento esto. Solo añaden a las listas creadas arriba.

 # el funcionamiento de este método es idéntico al de abrir carpeta normal, pero seleccionando la carpeta del listwidget_filtro y llevándote a la pestaña de descargas

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

 # Este método es un porro que nos colocamos (mentira fui yo solo pero no me quería sentir tan mal vale?) para darle un string a la etiqueta de los archivos que se quieren subir
 # El string que recibe es la lista de selecciones y cambiará según si se manda un solo archivo, 3 o más y ajustará las tabulaciones para que se vean los nombres

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

# Inicias de una puta vez y de verdad el programa, si falla se inicia sin conexión y si no funciona normal hasya que le des a la cruz

if __name__=='__main__':
    server_address = 'home500757070.1and1-data.host'
    try:
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
        app=QApplication(sys.argv)
        GUI= ejemploGUI(conexion)
        GUI.show()
        sys.exit(app.exec_())
    except:
         app=QApplication(sys.argv)
         GUI= ejemploGUI()
         GUI.show()
         sys.exit(app.exec_())
