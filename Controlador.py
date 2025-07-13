import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from Modelo import GestorCSV

class CSVControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = GestorCSV()
        self.conectar_eventos()

    def conectar_eventos(self):
        self.vista.btn_cargar.clicked.connect(self.cargar_csv)
        self.vista.btn_graficar.clicked.connect(self.graficar)

    def cargar_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(self.vista, "Selecciona un archivo CSV", "", "CSV files (*.csv)")
        if ruta:
            self.modelo.cargar_csv(ruta)
            columnas = self.modelo.obtener_columnas()
            self.vista.combo_x.clear()
            self.vista.combo_y.clear()
            self.vista.combo_x.addItems(columnas)
            self.vista.combo_y.addItems(columnas)
            self.mostrar_tabla()

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
