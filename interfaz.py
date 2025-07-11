from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem
)
from pymongo import MongoClient
from TRABAJO_FINAL import Usuario, ImagenMedica
import sys
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt

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

        self.layout = QVBoxLayout()

        self.btn_cargar = QPushButton("Seleccionar carpeta DICOM")
        self.btn_cargar.clicked.connect(self.seleccionar_carpeta)
        self.layout.addWidget(self.btn_cargar)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta DICOM")

        if carpeta:
            try:
                imagen = ImagenMedica(carpeta, coleccion_dicom)
                imagen.cargar_dicoms()
                imagen.guardar_en_mongo()
                metadatos = imagen.metadatos()

                self.btn_cargar.hide()

                # Limpiar widgets anteriores 
                while self.layout.count() > 1:
                    widget = self.layout.itemAt(1).widget()
                    if widget:
                        self.layout.removeWidget(widget)
                        widget.deleteLater()

                # Mostrar los metadatos nuevos
                for clave, valor in metadatos.items():
                    self.layout.addWidget(QLabel(f"{clave}: {valor}"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar la carpeta:\n{e}")


# Menú para expertos en señales
class SeñalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Señales")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        btn_csv = QPushButton("Visualizar CSV")
        btn_csv.clicked.connect(self.abrir_csv_view)
        layout.addWidget(btn_csv)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def abrir_csv_view(self):
        self.csv_view = CSVView()
        self.csv_view.show()
#Ventana principal 
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("aun no tiene nombre")
        self.setStyleSheet("""
    QWidget { background: white; font-family: Arial; font-size: 14px; }
    QPushButton {background: #4da6ff; color: white; border-radius: 5px; padding: 6px;}
    QPushButton:hover { background: #3399ff; }
    QLineEdit, QComboBox { border: 1px solid lightgray; border-radius: 4px; padding: 4px;}""")
        self.setGeometry(150, 150, 300, 300)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)
        self.mostrar_opciones_iniciales()

    def mostrar_opciones_iniciales(self):
        titulo = QLabel("Bienvenido a ...")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(titulo)
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
#Visualizar archivos csv 
class CSVView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Viewer")
        self.layout = QVBoxLayout()

        self.btn_cargar = QPushButton("Cargar CSV")
        self.btn_cargar.clicked.connect(self.cargar_csv)
        self.layout.addWidget(self.btn_cargar)

        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        self.layout.addWidget(QLabel("Columna X:"))
        self.layout.addWidget(self.combo_x)
        self.layout.addWidget(QLabel("Columna Y:"))
        self.layout.addWidget(self.combo_y)

        self.btn_graficar = QPushButton("Graficar Scatter")
        self.btn_graficar.clicked.connect(self.graficar)
        self.layout.addWidget(self.btn_graficar)

        self.btn_limpiar = QPushButton("Limpiar gráfico")
        self.btn_limpiar.clicked.connect(self.limpiar_grafico)
        self.layout.addWidget(self.btn_limpiar)

        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.df = None

    
    def cargar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
            return

        self.mostrar_tabla()
        self.llenar_combos()

    def mostrar_tabla(self):
        if self.df is None:
            return

        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                valor = str(self.df.iat[i, j])
                self.tabla.setItem(i, j, QTableWidgetItem(valor))

    def llenar_combos(self):
        self.combo_x.clear()
        self.combo_y.clear()

        columnas = list(self.df.columns)
        self.combo_x.addItems(columnas)
        self.combo_y.addItems(columnas)

    def graficar(self):
        if self.df is None:
            QMessageBox.warning(self, "Advertencia", "Primero debes cargar un archivo CSV.")
            return

        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()

        if not x_col or not y_col:
            QMessageBox.warning(self, "Advertencia", "Selecciona columnas X e Y.")
            return

        try:
            x = self.df[x_col]
            y = self.df[y_col]

            self.figure.clear()  # Limpiar gráfica anterior
            ax = self.figure.add_subplot(111)
            ax.scatter(x, y)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title("Gráfico de Dispersión")
            ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar:\n{e}")

    def limpiar_grafico(self):
        self.figure.clear()
        self.canvas.draw()

#Ejecutar la app 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
