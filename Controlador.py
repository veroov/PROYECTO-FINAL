import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
#importo las clases de los archivos modelo y vista
from Modelo import *
from vistaa import *

class Coordinador:
    def __init__(self, vista, modelo): #el controlador recibe todo de la vista y el modelo
        self.__mivista = vista
        self.__mimodelo = modelo
        self.conectar_eventos()

    def conectar_eventos(self):
        self.vista.btn_cargar.clicked.connect(self.cargar_csv)
        self.vista.btn_graficar.clicked.connect(self.graficar)

    def cargar_csv(self,ruta):
       return self.__mimodelo.cargar_csv(ruta) # como en el modelo se define esta función, aquí se llama y devuelve la información
     

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
