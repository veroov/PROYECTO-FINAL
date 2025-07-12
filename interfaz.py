from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from pymongo import MongoClient
from TRABAJO_FINAL import Usuario, ImagenMedica
import sys

# Ventana para experto en imágenes
class ImagenMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Imágenes")
        self.setGeometry(200, 200, 400, 300)

        self.label = QLabel("Bienvenido, experto en imágenes.\nCarga automática de imágenes DICOM realizada.")
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Conexión a la base de datos
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Bioingenieria"]
        coleccion_dicom = db["Dicom_nifti"]

        # Cargar carpeta DICOM 
        imagen = ImagenMedica("img1", coleccion_dicom)

        imagen.cargar_dicoms()
        metadatos = imagen.metadatos()
        imagen.guardar_en_mongo()

        # Mostrar metadatos
        for clave, valor in metadatos.items():
            layout.addWidget(QLabel(f"{clave}: {valor}"))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Ventana para experto en señales
class SenalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Señales")
        self.setGeometry(200, 200, 400, 200)
        label = QLabel("Bienvenido, experto en señales.\nAquí irán herramientas de análisis de señales.")
        layout = QVBoxLayout()
        layout.addWidget(label)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Ventana de Login
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login BioApp")
        self.setGeometry(150, 150, 300, 150)

        self.label_usuario = QLabel("Usuario:")
        self.input_usuario = QLineEdit()

        self.label_contra = QLabel("Contraseña:")
        self.input_contra = QLineEdit()
        self.input_contra.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.clicked.connect(self.verificar_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_contra)
        layout.addWidget(self.input_contra)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

        # Conexión a MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Bioingenieria"]
        self.coleccion_usuarios = db["Usuarios"]

    def verificar_login(self):
        username = self.input_usuario.text()
        password = self.input_contra.text()

        usuario = Usuario(username, password, None, self.coleccion_usuarios)
        valido, resultado = usuario.verificar()

        if valido:
            rol = resultado.strip().lower()
            QMessageBox.information(self, "Login exitoso", f"Bienvenido {usuario.usuario}, rol: {rol}")

            if rol == "imagenes":
                self.abrir_menu(ImagenMenu)
            elif rol == "señales":
                self.abrir_menu(SenalMenu)
            else:
                QMessageBox.warning(self, "Error", f"Rol desconocido: {rol}")
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")

    def abrir_menu(self, ventana_clase):
        self.hide()
        self.menu = ventana_clase()
        self.menu.show()

# Ejecución principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

