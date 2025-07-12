from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,QVBoxLayout, QMessageBox, QComboBox)
from pymongo import MongoClient
from TRABAJO_FINAL import Usuario, ImagenMedica
import sys

#Conexión global a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Bioingenieria"]
coleccion_usuarios = db["Usuarios"]
coleccion_dicom = db["Dicom_nifti"]

#Menú para expertos en imágenes
class ImagenMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Imágenes")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bienvenido, experto en imágenes.\nCarga automática de imágenes DICOM realizada."))

        imagen = ImagenMedica("img1", coleccion_dicom)
        imagen.cargar_dicoms()
        metadatos = imagen.metadatos()
        imagen.guardar_en_mongo()

        for clave, valor in metadatos.items():
            layout.addWidget(QLabel(f"{clave}: {valor}"))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Menú para expertos en señales
class SeñalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Señales")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bienvenido, experto en señales.\nAquí irán herramientas de análisis de señales."))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

#Ventana principal 
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("aun no tiene nombre")
        self.setGeometry(150, 150, 300, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mostrar_opciones_iniciales()

    def mostrar_opciones_iniciales(self):
        self.layout.addWidget(QLabel("Bienvenido a ..."))
        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.clicked.connect(self.mostrar_login)

        self.btn_registro = QPushButton("Registrarse")
        self.btn_registro.clicked.connect(self.mostrar_registro)

        self.layout.addWidget(self.btn_login)
        self.layout.addWidget(self.btn_registro)

    def mostrar_login(self):
        self.limpiar_layout()

        self.layout.addWidget(QLabel("Usuario:"))
        self.input_usuario = QLineEdit()
        self.layout.addWidget(self.input_usuario)

        self.layout.addWidget(QLabel("Contraseña:"))
        self.input_contra = QLineEdit()
        self.input_contra.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_contra)

        btn_confirmar = QPushButton("Entrar")
        btn_confirmar.clicked.connect(self.verificar_login)
        self.layout.addWidget(btn_confirmar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self.reiniciar)
        self.layout.addWidget(btn_volver)

    def mostrar_registro(self):
        self.limpiar_layout()

        self.layout.addWidget(QLabel("Nuevo usuario:"))
        self.input_usuario = QLineEdit()
        self.layout.addWidget(self.input_usuario)

        self.layout.addWidget(QLabel("Contraseña:"))
        self.input_contra = QLineEdit()
        self.input_contra.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_contra)

        self.layout.addWidget(QLabel("Rol:"))
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["imagenes", "señales"])
        self.layout.addWidget(self.combo_rol)

        btn_guardar = QPushButton("Registrar")
        btn_guardar.clicked.connect(self.registrar_usuario)
        self.layout.addWidget(btn_guardar)

        btn_volver = QPushButton("Volver")
        btn_volver.clicked.connect(self.reiniciar)
        self.layout.addWidget(btn_volver)

    def limpiar_layout(self):
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def reiniciar(self):
        self.limpiar_layout()
        self.mostrar_opciones_iniciales()

    def verificar_login(self):
        username = self.input_usuario.text().strip()
        password = self.input_contra.text().strip()

        usuario = Usuario(username, password, None, coleccion_usuarios)
        valido, resultado = usuario.verificar()

        if valido:
            rol = resultado.strip().lower()
            QMessageBox.information(self, "Login exitoso", f"Bienvenido {usuario.usuario}, rol: {rol}")
            if rol == "imagenes":
                self.abrir_menu(ImagenMenu)
            elif rol == "señales":
                self.abrir_menu(SeñalMenu)
            else:
                QMessageBox.warning(self, "Error", f"Rol desconocido: {rol}")
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")

    def registrar_usuario(self):
        usuario = self.input_usuario.text().strip()
        contra = self.input_contra.text().strip()
        rol = self.combo_rol.currentText()

        if not usuario or not contra:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        nuevo = Usuario(usuario, contra, rol, coleccion_usuarios)
        exito, mensaje = nuevo.guardar()

        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.reiniciar()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def abrir_menu(self, ventana_clase):
        self.hide()
        self.menu = ventana_clase()
        self.menu.show()

#Ejecutar la app 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
