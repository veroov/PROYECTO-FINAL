import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QApplication
from Vista import *
from Modelo import (
    Usuario, ImagenMedica, ProcesadorImagen, GestorSeñales, GestorCSV, RegistroArchivo,
    coleccion_usuarios, coleccion_dicom, coleccion_archivos
)
from Vista import LoginWindow
import sys

#la ventana ya no se abre en vista, porque investigue y se debia abrir desde el controlador
class Coordinador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.procesador = None
        self.senal_modelo = GestorSeñales()

        self.imagen_medica = None

    #recibe los datos del usuario desde la vista y los pasa al modelo
    def verificar_login(self, usuario, contraseña): #pasa como parametros el usuario y la contraseña 
        modelo = Usuario(usuario, contraseña, "", coleccion_usuarios)# crea un objeto Usuario con los datos ingresados
        return modelo.verificar() #devuelve el resultado de la verificación

      
#selecciona la carpeta DICOM y carga los archivos DICOM en la base de datos
    def seleccionar_archivo(self, carpeta):
        self.imagen_medica = ImagenMedica(carpeta, coleccion_dicom)
        return self.imagen_medica.cargar_dicoms() 
    
    def metadatos_dicom(self, carpeta): #Obtiene los metadatos de la imagen médica
        return self.imagen_medica.metadatos()
    
    def guardar_paciente(self, carpeta): #carpeta está presente porque está en imagenMedica como parametro, si lo quito sale error
        return self.imagen_medica.guardar_paciente()

    def obtener_corte(self, eje, indice, carpeta):
        return self.imagen_medica.obtener_corte(eje, indice)

    def obtener_dimensiones(self, carpeta):
        return self.imagen_medica.obtener_dimensiones_volumen()
    
    def convertir_a_nifti_y_guardar(self, carpeta, ruta_salida):
        return self.imagen_medica.convertir_a_nifti_y_guardar(ruta_salida)

    def cargar_mat(self, ruta):
        # El controlador usa su instancia del gestor de señales para cargar el archivo.
        llaves = self.gestor_senales.cargar_mat(ruta)
        nombre_archivo = os.path.basename(ruta)
        registro = RegistroArchivo("mat", nombre_archivo, ruta, coleccion_archivos)
        registro.guardar()
        return llaves
    
    def obtener_senal(self, llave):
        return self.gestor_senales.obtener_senal(llave)    

    def calcular_promedio_eje1(self, array_3d):
        """
        Calcula el promedio a lo largo del eje 1 (muestras).
        Devuelve un array 2D con la forma (ensayos, canales).
        """
        if array_3d is None or array_3d.ndim != 3:
            return None
        # Se usa np.mean de NumPy con axis=1 para promediar sobre el eje de las muestras.
        return np.mean(array_3d, axis=1)
    
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
    
    def procesar_imagen(self, ruta, accion, tam_kernel=5, umbral=127):
        self.procesador = ProcesadorImagen(ruta)

        if accion == "gris":
            img = self.procesador.cambiar_espacio_color("gris")
        elif accion == "hsv":
            img = self.procesador.cambiar_espacio_color("hsv")
        elif accion == "ecualizar":
            img = self.procesador.ecualizar()
        elif accion == "binarizar":
            img = self.procesador.binarizar(umbral=umbral)
        elif accion == "apertura":
            img = self.procesador.operacion_morfologica("apertura", tam_kernel=tam_kernel)
        elif accion == "cierre":
            img = self.procesador.operacion_morfologica("cierre", tam_kernel=tam_kernel)
        elif accion == "invertir":
            img = self.procesador.invertir_imagen()
        elif accion == "contar":
            total = self.procesador.contar_celulas()
            return None, total  # Solo retorna el conteo
        else:
            raise ValueError(f"Acción '{accion}' no reconocida.")
        return img, None
    
    def cargar_csv(self, ruta):
        gestor = GestorCSV()
        gestor.cargar_csv(ruta)
        return gestor

    def obtener_columnas_csv(self, gestor):
        return gestor.obtener_columnas()

    def obtener_datos_columnas(self, gestor, col_x, col_y):
        return gestor.obtener_datos_columnas(col_x, col_y)

    def registrar_csv(self, ruta):
        nombre = os.path.basename(ruta)
        registro = RegistroArchivo("csv", nombre, ruta,coleccion_archivos)
        registro.guardar()

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
