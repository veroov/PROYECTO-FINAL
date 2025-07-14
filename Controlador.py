import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from Modelo import *
from Vista import *


class Coordinador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.conectar_eventos()

    def conectar_eventos(self):
        self.vista.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.vista.btn_graficar.clicked.connect(self.graficar)

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