
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel
)

####
class CSVView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Viewer")
        self.layout = QVBoxLayout()

        self.btn_cargar = QPushButton("Cargar CSV")
        self.layout.addWidget(self.btn_cargar)

        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        self.layout.addWidget(QLabel("Columna X:"))
        self.layout.addWidget(self.combo_x)
        self.layout.addWidget(QLabel("Columna Y:"))
        self.layout.addWidget(self.combo_y)

        self.btn_graficar = QPushButton("Graficar Scatter")
        self.layout.addWidget(self.btn_graficar)

        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        self.setLayout(self.layout)
