import sys
import time
from pathlib import Path
from tkinter import messagebox
from tkinter.simpledialog import askstring

import pysftp
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QImage, QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QPushButton, QListWidgetItem

server_address = 'home500757070.1and1-data.host'
VERSION = "v.1.0.0-alpha"


class EjemploGUI(QMainWindow):
    """
    El directorio por defecto para las descargas es la carpeta DescagasBEST que se crea en la
    misma carpeta que el ejecutable
    """
    download_dir = Path("./DescargasBEST")
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    def __init__(self):
        super().__init__()
        self.label_archivo_elegido = ""
        self.download_dir.mkdir(exist_ok=True)
        uic.loadUi("Menu.ui", self)
        self.cancelar.setEnabled(False)
        self.archivos.clicked.connect(self.browsefiles)
        self.cancelar.clicked.connect(self.cancelar_subida)
        self.try_conexion.clicked.connect(self.probar_conex)
        self.archivo_subir = None
        self.archivos.setText("Examinar")
        self.joseluis = QPushButton("PyQt5 button")
        self.listWidget.itemClicked.connect(self.seleccionar)
        self.bdescarga.clicked.connect(self.descargar)
        self.lista_online = list()
        self.directorio_actual = '/'
        self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
        self.bdescarga.setEnabled(False)
        self.try_conexion_2.clicked.connect(self.probar_conex2)
        self.archivos_dir = []
        self.carpetas_dir = list()
        self.mostrar_logo_best(self.logo_best)
        self.mostrar_logo_best(self.logo_best2)
        self.babrir_carpeta.clicked.connect(self.abrir_carpeta)
        self.babrir_carpeta.setEnabled(False)
        self.volver_atras.setEnabled(False)
        self.volver_atras.clicked.connect(self.carpeta_anterior)
        self.bnueva_carpeta.clicked.connect(self.crear_carpeta)
        self.b_cambiarnom.clicked.connect(self.renombrar)
        self.brecilaje.clicked.connect(self.mover_reciclaje)
        self.listWidget.itemDoubleClicked.connect(self.seleccionar_carpeta)
        self.lineEdit_carpeta.setText("Nueva_Carpeta")
        self.lineEdit_carpeta.installEventFilter(self)
        self.conexion = pysftp.Connection(server_address, username="u1881262367", password="FreeSpace420",
                                          cnopts=EjemploGUI.cnopts)

    def subida(self):

        self.etiqueta2.setText("")
        self.etiqueta.setText("")
        try:
            with self.conexion.cd(self.directorio_actual):  # temporarily chdir to public
                self.conexion.put(self.archivo_subir)
                # conexion.get('mapa1.png')
                # print(self.conexion.listdir())
                self.cancelar_subida()
                self.probarlista()
        except:
            self.etiqueta2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def probar_conex(self):
        self.etiqueta2.setText("Probando...")
        self.archivos.setEnabled(False)
        self.try_conexion.setEnabled(False)
        time.sleep(1)
        self.archivos.setEnabled(True)
        self.try_conexion.setEnabled(True)

        try:
            self.etiqueta2.setText("\t\tConexión establecida satisfactoriamente.")
        except:
            self.etiqueta2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def probar_conex2(self):
        self.etiqueta2_2.setText("Probando...")
        self.try_conexion_2.setEnabled(False)
        time.sleep(1)
        self.try_conexion_2.setEnabled(True)
        try:
            self.etiqueta2_2.setText("\t\tConexión establecida satisfactoriamente.")
        except:
            self.etiqueta2_2.setText("Ha habido algún error. Asegúrate de pagar el wifi antes de volver a intentarlo.")

    def cancelar_subida(self):
        self.cancelar.setEnabled(False)
        self.archivos.setEnabled(True)
        self.archivo_subir = None
        self.archivos.clicked.connect(self.browsefiles)
        self.archivos.clicked.disconnect(self.subida)
        self.archivos.setText("Examinar")
        self.prefoto.clear()
        self.etiqueta2.setText("")
        self.etiqueta.setText("")

    def browsefiles(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', r'C:\Users\Usuario\Desktop', 'PNG files (*.png)')
        if fname[0] != '':
            self.etiqueta.setText(f'Archivo seleccionado\t(Se muestra la ruta completa a continuación.)\n\n{fname[0]}')
            self.archivo_subir = fname[0]
            self.cancelar.setEnabled(True)
            self.archivos.clicked.disconnect(self.browsefiles)
            self.archivos.clicked.connect(self.subida)
            self.archivos.setText("Subir archivo")
            self.mostrar_imagen()
        else:
            self.etiqueta.setText("No se ha seleccionado ningún archivo.")

    def probarlista(self):

        self.listWidget.clear()
        try:
            with self.conexion.cd(self.directorio_actual):  # temporarily chdir to public
                # conexion.get('mapa1.png')
                lista = self.conexion.listdir()
                self.archivos_dir = []
                self.carpetas_dir = list()
                for nombre in lista:
                    if nombre != 'Reciclaje':
                        if nombre[-4] != '.':
                            self.carpetas_dir.append(nombre)
                        else:
                            self.archivos_dir.append(nombre)
                try:
                    for i in self.carpetas_dir:
                        item_carpeta = QListWidgetItem(i)
                        item_carpeta.setIcon(QIcon("carpeta.png"))
                        self.listWidget.addItem(item_carpeta)
                except:
                    for i in self.carpetas_dir: self.listWidget.addItem(i)
                try:
                    for i in self.archivos_dir:
                        item_archivo = QListWidgetItem(i)
                        item_archivo.setIcon(QIcon("Iconoarchivo.png"))
                        self.listWidget.addItem(item_archivo)

                except:
                    for i in self.archivos_dir: self.listWidget.addItem(i)


        except:
            self.label_3.setText(
                f"Ha habido un error al mostrar los archivos contenidos en la carpeta:  {self.directorio_actual}")

    def seleccionar(self, lstItem):
        self.label_archivo_elegido.setText(f'Has elegido: {lstItem.text()}')
        self.archivo_descargar = lstItem.text()
        self.bdescarga.setEnabled(True)
        if self.archivo_descargar in self.carpetas_dir:
            self.babrir_carpeta.setEnabled(True)
        else:
            self.babrir_carpeta.setEnabled(False)

    def descargar(self):
        self.label_archivo_elegido.setText('')
        with self.conexion.cd(self.directorio_actual):  # temporarily chdir to public
            """conexion.get_r(self.archivo_descargar,'.')"""
            pordescargar = self.directorio_actual + '/' + self.archivo_descargar
            local = Path(f"{self.download_dir}/{self.archivo_descargar}")

            self.conexion.get(pordescargar, local)
            """messagebox.showerror("Error",f"Actual: {pordescargar} Objetivo:{local}")"""
            self.bdescarga.setEnabled(False)
            self.label_archivo_elegido.setText(f'DESCARGADO: {self.archivo_descargar}')
            self.archivo_descargar = None

    def mostrar_imagen(self):
        try:
            imagen_predeterminada = self.archivo_subir
            image = QImage(imagen_predeterminada)
            self.prefoto.setPixmap(QPixmap.fromImage(image))
            self.prefoto.setScaledContents(True)
        except:
            self.label_archivo_elegido.setText("No se ha podido previsualizar el archivo.")

    def mostrar_logo_best(self, objeto):
        try:
            imagen_predeterminada = 'Logo_apli.png'
            image = QImage(imagen_predeterminada)
            objeto.setPixmap(QPixmap.fromImage(image))
            objeto.setScaledContents(True)
        except:
            pass

    def abrir_carpeta(self):
        if self.directorio_actual == '/':
            # print(self.archivo_descargar)
            self.directorio_actual += self.archivo_descargar
        else:
            self.directorio_actual += '/' + self.archivo_descargar
        self.archivo_descargar = None
        self.probarlista()
        self.babrir_carpeta.setEnabled(False)
        self.volver_atras.setEnabled(True)
        self.label_archivo_elegido.setText('')
        self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")

    def dir_padre(self, directorio):
        indice_barra = directorio.rfind("/")
        directorio_padre = directorio[:indice_barra]
        return directorio_padre

    def carpeta_anterior(self):
        if self.directorio_actual != '/' and self.dir_padre(self.directorio_actual) != '':
            self.directorio_actual = self.dir_padre(self.directorio_actual)
        else:
            self.directorio_actual = '/'
        if self.directorio_actual == '/':
            self.volver_atras.setEnabled(False)
        self.label_archivo_elegido.setText('')

        self.probarlista()
        self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")

    def seleccionar_carpeta(self, lstItem):
        self.nombre_archivo = lstItem.text()
        if self.nombre_archivo[-4] != '.':
            self.abrir_carpeta()

    def crear_carpeta(self):
        nombre_carpeta = self.lineEdit_carpeta.text()
        self.lineEdit_carpeta.clear()
        if not nombre_carpeta: nombre_carpeta = "Nueva_Carpeta"
        try:
            if self.directorio_actual != '/':
                nueva = self.directorio_actual + '/' + nombre_carpeta
            else:
                nueva = self.directorio_actual + nombre_carpeta
            if (self.conexion.isdir(nueva)):
                messagebox.showerror("Error", "Nombre de la carpeta ya en uso")
            else:
                self.conexion.makedirs(nueva)
                self.directorio_actual = nueva
                self.label_3.setText(f"Estás en esta carpeta: {self.directorio_actual}")
                self.probarlista()
                self.volver_atras.setEnabled(True)

        except:
            messagebox.showerror("Errorcito", "Ni lo has intentado")

    def renombrar(self):
        try:

            nombre_carpeta = askstring('Renombrar', 'Inserta el nuevo nombre')
            if self.directorio_actual != '/':
                nueva = self.directorio_actual + '/' + nombre_carpeta
                vieja = self.directorio_actual + '/' + self.archivo_descargar
            else:
                nueva = self.directorio_actual + nombre_carpeta
                vieja = self.directorio_actual + self.archivo_descargar
            self.conexion.rename(vieja, nueva)
            self.probarlista()

        except:
            messagebox.showerror("Error", "Algo ha salido mal")

    def mover_reciclaje(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        try:
            if self.directorio_actual != '/':
                objetivo = "Reciclaje/" + self.archivo_descargar
                actual = self.directorio_actual + '/' + self.archivo_descargar
            else:
                objetivo = "Reciclaje" + self.directorio_actual + self.archivo_descargar
                actual = self.directorio_actual + self.archivo_descargar

            while (self.conexion.isdir(objetivo)):
                self.archivo_descargar = 'Copia_' + self.archivo_descargar
                objetivo = "Reciclaje" + '/' + self.archivo_descargar

            while (self.conexion.isfile(objetivo)):
                self.archivo_descargar = 'Copia_' + self.archivo_descargar
                objetivo = "Reciclaje" + '/' + self.archivo_descargar

            self.conexion.rename(actual, objetivo)
            self.probarlista()

        except:
            messagebox.showerror("Error", "Algo ha salido mal")

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.lineEdit_carpeta:
            if event.key() == QtCore.Qt.Key_Return and self.lineEdit_carpeta.hasFocus():
                self.crear_carpeta()
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = EjemploGUI()
    GUI.show()
    GUI.probarlista()
    sys.exit(app.exec_())
