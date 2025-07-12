from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import pandas as pd
import numpy as np
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

client = MongoClient("mongodb://localhost:27017/")
db = client["Bioingenieria"]
coleccion_usuarios = db["Usuarios"]

class Usuario:
    def __init__(self, usuario, contraseña, rol="señales"):
        self.usuario = usuario
        self.contraseña = contraseña
        self.rol = rol

    def verificar(self):
        usuario = coleccion_usuarios.find_one({
            "usuario": self.usuario,
            "contraseña": self.contraseña
        })
        if usuario:
            return True, usuario["rol"]
        return False, "datos incorrectos."

class VisualizadorSenal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualización de Señal - Usuario Experto")
        self.setGeometry(200, 200, 800, 600)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.btn_senal = QPushButton("Mostrar Señal Senoidal")
        self.btn_senal.clicked.connect(self.mostrar_senal)
        layout.addWidget(self.btn_senal)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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

class LoginDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Usuario:"))
        self.input_user = QLineEdit()
        layout.addWidget(self.input_user)

        layout.addWidget(QLabel("Contraseña:"))
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_pass)

        btn = QPushButton("Ingresar")
        btn.clicked.connect(self.verificar)
        layout.addWidget(btn)

        self.setLayout(layout)

    def verificar(self):
        user = self.input_user.text().strip()
        pw = self.input_pass.text().strip()
        u = Usuario(user, pw)
        valido, rol = u.verificar()

        if valido:
            if rol == "señales":
                self.hide()
                self.ventana = VisualizadorSenal()
                self.ventana.show()
            elif rol == "imagenes":
                QMessageBox.information(self, "Info", "Usuario de imágenes. Abre otro módulo.")
            else:
                QMessageBox.warning(self, "Error", f"Rol desconocido: {rol}")
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = LoginDemo()
    ventana.show()
    sys.exit(app.exec_())
