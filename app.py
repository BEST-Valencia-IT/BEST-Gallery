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
 
server_address = 'home500757070.1and1-data.host'

class ejemploGUI(QMainWindow):

    def __init__(self,conex=None):
        super().__init__()
        self.conexion=conex
        uic.loadUi("Menu.ui",self)
        self.setFixedSize(self.size())
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

    def iniciar(self):
            print('iniciar')
            self.b_cambiarnom.setEnabled(False)
            self.cancelar.setEnabled(False)
            self.archivos.clicked.connect(self.browsefiles)
            self.cancelar.clicked.connect(self.cancelar_subida)
            self.try_conexion.clicked.connect(self.probar_conex)
            self.archivo_subir=None
            self.archivos.setText("Examinar")
            self.joseluis = QPushButton("PyQt5 button")
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
            self.lineEdit_carpeta.setText("")
            self.lineEdit_carpeta.installEventFilter(self)
            self.probarlista()
            self.bnueva_carpeta.setEnabled(True)
            self.b_cambiarnom.setEnabled(False)
            self.archivos.setEnabled(True)
            self.ir_dir_filtro.setEnabled(False)
            self.ir_dir_filtro.clicked.connect(self.abrir_carpeta_filtro)
            self.Buscar_filtro.clicked.connect(self.filtrar)
            self.lista_filtro.itemClicked.connect(self.seleccionar_filtro)

    def subida(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        self.etiqueta2.setText("")
        self.etiqueta.setText("")
        try:
                with self.conexion.cd(self.directorio_actual):
                    for i in self.archivo_subir[:-1]:
                        self.conexion.put(i)
                    #conexion.get('mapa1.png')
                    self.cancelar_subida()
                    self.probarlista()
                    self.tabWidget.setCurrentIndex(0)
        except:
            self.etiqueta2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def probar_conex(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        try:
                conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
                self.conexion=conexion
                self.iniciar()

        except:
            self.etiqueta2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def probar_conex2(self):
        cnopts=pysftp.CnOpts()
        cnopts.hostkeys=None
        try:
                conexion= pysftp.Connection(server_address,username ="u1881262367",password="FreeSpace420",cnopts=cnopts)
                self.conexion=conexion
                self.iniciar()
        except:
            self.etiqueta2_2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def cancelar_subida(self):
        self.cancelar.setEnabled(False)
        self.archivos.setEnabled(True)
        self.archivo_subir=None
        self.archivos.clicked.connect(self.browsefiles)
        self.archivos.clicked.disconnect(self.subida)
        self.archivos.setText("Examinar")
        self.prefoto.clear()
        self.etiqueta2.setText("")
        self.etiqueta.setText("")


    def browsefiles(self):
        fname=QFileDialog.getOpenFileNames(self,'Open file')
        if fname[0]!='':
            print(fname[0])
            a=self.generar_string(fname[0])
            self.etiqueta.setText(f'Archivos y ruta de los archivos:\n\n{a}')
            self.archivo_subir=fname[0]
            self.cancelar.setEnabled(True)
            self.archivos.clicked.disconnect(self.browsefiles)
            self.archivos.clicked.connect(self.subida)
            self.archivos.setText("Subir archivo")
            self.mostrar_imagen()
        else:
            self.etiqueta.setText("No se ha seleccionado ningún archivo.")

    def probarlista(self):
        print('Probar lista')
        self.listWidget.clear()
        try:
                with self.conexion.cd(self.directorio_actual):             # temporarily chdir to public
                    print('Pasa el try de probar lista')
                    #conexion.get('mapa1.png')
                    lista=self.conexion.listdir()
                    print(lista)
                    self.archivos_dir=[]
                    self.carpetas_dir=list()
                    for nombre in lista:
                        if nombre!='Reciclaje':
                            if self.conexion.isdir(nombre)==True:
                                self.carpetas_dir.append(nombre)
                            else: self.archivos_dir.append(nombre)
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
        except:
            self.label_3.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_4.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
            self.label_5.setText(f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")
        self.b_cambiarnom.setEnabled(False)

    def seleccionar(self,lstItem):
        self.label_archivo_elegido.setText(f'Has elegido: {lstItem.text()}')
        self.archivo_descargar=lstItem.text()
        self.bdescarga.setEnabled(True)
        self.b_cambiarnom.setEnabled(True)
        if self.archivo_descargar in self.carpetas_dir:
            self.babrir_carpeta.setEnabled(True)
        else: self.babrir_carpeta.setEnabled(False)

    def descargar(self):
        try:
            directorio_destino = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta de destino")
            print(directorio_destino)
            if directorio_destino:
                if conexion.isdir(self.archivo_descargar):
                    pordescargar=self.directorio_actual+self.archivo_descargar
                    ruta_local= os.path.join(directorio_destino,self.archivo_descargar)
                    ruta_local=ruta_local.replace("/","\\")
                    self.conexion.get_r(pordescargar,directorio_destino)
                    self.label_archivo_elegido.setText('')
                    self.bdescarga.setEnabled(False)
                    self.label_archivo_elegido.setText(f'DESCARGADO: {self.archivo_descargar}')
                    self.archivo_descargar=None
                else:
                    with self.conexion.cd(self.directorio_actual):             # temporarily chdir to public
                        """conexion.get_r(self.archivo_descargar,'.')"""
                        print('Establece conexión')

                        if self.directorio_actual!='/':
                            pordescargar=self.directorio_actual+'/'+self.archivo_descargar

                        else:
                            pordescargar=self.directorio_actual+self.archivo_descargar
                        self.conexion.get(pordescargar,localpath=os.path.join(directorio_destino,self.archivo_descargar))
                        """messagebox.showerror("Error",f"Actual: {pordescargar} Objetivo:{local}")"""
                        self.label_archivo_elegido.setText('')
                        self.bdescarga.setEnabled(False)
                        self.label_archivo_elegido.setText(f'DESCARGADO: {self.archivo_descargar}')

                        self.archivo_descargar=None
        except:
               self.label_archivo_elegido.setText('Ha habido un fallo al descargar. Una posible razón es que exista un archivo con el mismo nombre (y que ya lo hayas descargado).')

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

    def mostrar_logo_best(self,objeto):
        try:
            imagen_predeterminada = 'Logo_apli.png'
            image = QImage(imagen_predeterminada)
            objeto.setPixmap(QPixmap.fromImage(image))
            objeto.setScaledContents(True)
        except: pass

    def abrir_carpeta(self):
            if self.directorio_actual=='/':
                print(self.archivo_descargar)
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

    def dir_padre(self,directorio):
        indice_barra = directorio.rfind("/")
        directorio_padre = directorio[:indice_barra]
        return directorio_padre

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

    def seleccionar_carpeta(self,lstItem):
        self.nombre_archivo=lstItem.text()
        with self.conexion.cd(self.directorio_actual):
            if self.conexion.isdir(self.nombre_archivo):
                self.abrir_carpeta()

    def crear_carpeta(self):
        nombre_carpeta=self.lineEdit_carpeta.text()
        self.lineEdit_carpeta.clear()
        if not nombre_carpeta: nombre_carpeta="Nueva_Carpeta"
        try:
                if self.directorio_actual!='/': nueva=self.directorio_actual+'/'+nombre_carpeta
                else:nueva=self.directorio_actual+nombre_carpeta
                if(self.conexion.isdir(nueva)==True):
                    messagebox.showerror("Error", "Nombre de la carpeta ya en uso aquí")
                else:
                    self.conexion.makedirs(nueva)
                    self.directorio_actual=nueva
                    self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                    self.probarlista()
                    self.volver_atras.setEnabled(True)

        except:
            messagebox.showerror("Errorcito", "Ni lo has intentado")

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
                self.probarlista()
                self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                self.label_4.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                self.label_5.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        except:
            messagebox.showerror("Error","Nombre de la carpeta ya en uso aquí")

    def mover_reciclaje(self):
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
        except:
            messagebox.showerror("Error","Algo ha salido mal")


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.lineEdit_carpeta:
            if event.key() == QtCore.Qt.Key_Return and self.lineEdit_carpeta.hasFocus():
                self.crear_carpeta()
        return super().eventFilter(obj, event)

    def filtrar(self):
        nombre_buscar=self.lineEdit_filtro.text()
        self.lista_filtro.clear()
        if nombre_buscar!='' and len(nombre_buscar)>3:
                self.lista_rutas=list()
                try:
                    self.archivos_dir=[]
                    self.carpetas_dir=list()
                    conexion.walktree('/',fcallback=self.añadir_fwalktree, dcallback=self.añadir_dirwalktree, ucallback=self.nada)
                    for ruta in self.lista_rutas:
                        indice_barra = ruta.rfind("/")
                        archivo = ruta[indice_barra+1:]
                        if nombre_buscar in archivo and 'Reciclaje' not in ruta:
                            if self.conexion.isdir(ruta)==True:
                                self.carpetas_dir.append(ruta)
                            else: self.archivos_dir.append(ruta)
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
                    self.ir_dir_filtro.setEnabled(True)
                except: print('Ha habido un error, probablemente de conexión')

    def añadir_fwalktree(self,filename): self.lista_rutas.append(filename)
    def añadir_dirwalktree(self,dirname): self.lista_rutas.append(dirname)
    def nada(self): pass

    def abrir_carpeta_filtro(self):
        destino=self.archivo_filtrar
        print(destino)
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
        except: print('Ha habido un error')

    def seleccionar_filtro(self, item):
         self.archivo_filtrar=item.text()
         print(self.archivo_filtrar)

    def generar_string(self,fname):
        if len(fname)==1:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            return f"{ruta}\t{fname[0][indice_barra+1:]}"
        elif len(fname)>=3:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            for i in range(0,3):
                    ruta+=f"\t{fname[i][indice_barra+1:]}"
            ruta+="\n\t\t..."
        else:
            ruta=f"{self.dir_padre(fname[0])}\n\n"
            indice_barra = fname[0].rfind("/")
            for i in fname:
                ruta+=f"\t{i[indice_barra+1:]}"
        return ruta


if __name__=='__main__':
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
