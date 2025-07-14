import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from Modelo import *
from Vista import *

#la ventana ya no se abre en vista, porque investigue y se debia abrir desde el controlador
class Coordinador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo

    #recibe los datos del usuario desde la vista y los pasa al modelo
    def verificar_login(self, usuario, contraseña): #pasa como parametros el usuario y la contraseña 
        modelo = Usuario(usuario, contraseña, "", coleccion_usuarios)# crea un objeto Usuario con los datos ingresados
        return modelo.verificar() #devuelve el resultado de la verificación

    def seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(self.vista, "Selecciona un archivo CSV", "", "CSV files (*.csv)")
        if ruta:
            self.cargar_csv(ruta)
            columnas = self.modelo.obtener_columnas()
            self.vista.combo_x.clear()
            self.vista.combo_y.clear()
            self.vista.combo_x.addItems(columnas)
            self.vista.combo_y.addItems(columnas)
            self.mostrar_tabla()

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