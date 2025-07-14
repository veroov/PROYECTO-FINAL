import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from Modelo import *
from Vista import *


#la ventana ya no se abre en vista, porque investigue y se debia abrir desde el controlador
class Coordinador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.procesador = None
        self.senal_modelo = GestorSeñales()
        self.conectar_eventos()

        self.imagen_medica = None

    #recibe los datos del usuario desde la vista y los pasa al modelo
    def verificar_login(self, usuario, contraseña): #pasa como parametros el usuario y la contraseña 
        modelo = Usuario(usuario, contraseña, "", coleccion_usuarios)# crea un objeto Usuario con los datos ingresados
        return modelo.verificar() #devuelve el resultado de la verificación
    
#selecciona la carpeta DICOM y carga los archivos DICOM en la base de datos
    def seleccionar_archivo(self, carpeta):
        self.imagen_medica = ImagenMedica(carpeta, coleccion_dicom)
        return self.imagen_medica.cargar_dicoms() and self.imagen_medica.guardar_en_mongo()

    def metadatos_dicom(self, carpeta): #Obtiene los metadatos de la imagen médica
        return self.imagen_medica.metadatos()

    def obtener_corte(self, eje, indice, carpeta):
        return self.imagen_medica.obtener_corte(eje, indice)

    def obtener_dimensiones(self, carpeta):
        return self.imagen_medica.obtener_dimensiones_volumen()
    


    def cargar_csv(self, ruta):
        self.modelo.cargar_csv(ruta)
        nombre = os.path.basename(ruta)
        registro = RegistroArchivo("csv", nombre, ruta, coleccion_archivos)
        registro.guardar()
        

    def mostrar_tabla(self):
        df = self.modelo.obtener_datos()
        self.vista.tabla.setRowCount(len(df))
        self.vista.tabla.setColumnCount(len(df.columns))
        self.vista.tabla.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.vista.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def graficar(self):
        x = self.vista.combo_x.currentText()
        y = self.vista.combo_y.currentText()
        self.modelo.graficar_dispersion(x, y, plt)
        plt.show()
    
      def cargar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self.vista, "Seleccionar imagen", "", "Imagenes (*.jpg *.png)")
        if ruta:
            self.procesador = ProcesadorImagen(ruta)
            self.mostrar_imagen(self.procesador.original)

            # Registrar en MongoDB
            nombre = os.path.basename(ruta)
            tipo = os.path.splitext(nombre)[1].replace(".", "")  # jpg o png
            registro = RegistroArchivo(tipo, nombre, ruta, coleccion_archivos)
            registro.guardar()

            self.vista.imagen_path = ruta  # Guardar la ruta por si la necesitas

    def procesar_imagen(self):
        if not self.procesador:
            QMessageBox.warning(self.vista, "Advertencia", "Primero debes cargar una imagen.")
            return

        accion = self.vista.combo_accion.currentText().lower()

        if accion == "gris":
            img = self.procesador.cambiar_espacio_color("gris")
        elif accion == "hsv":
            img = self.procesador.cambiar_espacio_color("hsv")
        elif accion == "ecualizar":
            img = self.procesador.ecualizar()
        elif accion == "binarizar":
            img = self.procesador.binarizar()
        elif accion == "apertura":
            img = self.procesador.operacion_morfologica("apertura")
        elif accion == "cierre":
            img = self.procesador.operacion_morfologica("cierre")
        elif accion == "invertir":
            img = self.procesador.invertir_imagen()
        elif accion == "contar células":
            total = self.procesador.contar_celulas()
            QMessageBox.information(self.vista, "Resultado", f"Se detectaron {total} objetos/células.")
            return
        elif accion == "segmentar k-means":
            img = self.procesador.segmentar_kmeans()
        else:
            QMessageBox.warning(self.vista, "Acción desconocida", "La acción seleccionada no es válida.")
            return 
        self.mostrar_imagen(img)

 def cargar_mat(self):
        ruta, _ = QFileDialog.getOpenFileName(self.vista, "Selecciona un archivo .mat", "", "Archivos MAT (*.mat)")
        if ruta:
            llaves = self.senal_modelo.cargar_mat(ruta)
            if not llaves:
                QMessageBox.warning(self.vista, "Archivo inválido", "No se encontraron señales válidas en el archivo.")
                return
            self.vista.combo_llaves.clear()
            self.vista.combo_llaves.addItems(llaves)

            nombre = os.path.basename(ruta)
            registro = RegistroArchivo("mat", nombre, ruta, coleccion_archivos)
            registro.guardar()
            self.vista.label_estado.setText(f"Archivo cargado: {nombre}")

    def graficar_senal(self):
        llave = self.vista.combo_llaves.currentText()
        if not llave:
            return
        senal = self.senal_modelo.obtener_senal(llave)
        if senal is None:
            QMessageBox.warning(self.vista, "Error", "No se pudo extraer la señal.")
            return

        self.vista.ax.clear()
        self.vista.ax.plot(senal)
        self.vista.ax.set_title(f"Señal: {llave}")
        self.vista.canvas.draw()
        
    def conectar_eventos(self):
        if hasattr(self.vista, 'btn_cargar'): #hasattr evalua si el objeto, tiene el atributo especificado 
            self.vista.btn_cargar.clicked.connect(self.cargar_imagen)
        if hasattr(self.vista, 'btn_procesar'):
            self.vista.btn_procesar.clicked.connect(self.procesar_imagen)
        if hasattr(self.vista, 'btn_cargar_mat'):
            self.vista.btn_cargar_mat.clicked.connect(self.cargar_mat)
        if hasattr(self.vista, 'combo_llaves'):
            self.vista.combo_llaves.currentIndexChanged.connect(self.graficar_senal)
def main():
    app = QApplication(sys.argv)

    vista = LoginWindow()
    modelo = Usuario("nombre", "clave", "rol", coleccion_usuarios)  # O lo que necesite tu lógica

    coordinador = Coordinador(vista, modelo)
    vista.asignarCoordinador(coordinador)

    vista.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
