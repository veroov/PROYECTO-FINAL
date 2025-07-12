# visualizador_senal.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class VisualizadorSenal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualización de Señal - Usuario Experto")
        self.setGeometry(200, 200, 800, 600)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.mostrar_senal()

    def mostrar_senal(self):
        ax = self.canvas.figure.subplots()
        ax.clear()
        t = np.linspace(0, 1, 500)
        senal = np.sin(2 * np.pi * 10 * t)
        ax.plot(t, senal, label="Señal Senoidal")
        ax.set_title("Señal simulada")
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel("Amplitud")
        ax.legend()
        self.canvas.draw()
