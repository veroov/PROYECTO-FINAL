import sys
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QSlider, QRadioButton, QButtonGroup, QGroupBox
)
from PyQt5.QtCore import Qt
from Modelo import Usuario, ImagenMedica
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.io import loadmat
import cv2
from Modelo import coleccion_usuarios, coleccion_dicom

#Clase ImagenMenu 
class ImagenMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Visualizador de Imágenes DICOM")
        self.setGeometry(100, 100, 800, 600)
        
        self.imagen_medica = None # Objeto para manejar la lógica DICOM

        #Layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout_principal = QHBoxLayout(main_widget)

        #Panel de controles (Izquierda) 
        panel_controles = QWidget()
        panel_controles.setFixedWidth(250)
        self.layout_controles = QVBoxLayout(panel_controles)
        self.layout_controles.setAlignment(Qt.AlignTop)

        self.btn_cargar = QPushButton("Seleccionar Carpeta DICOM")
        self.btn_cargar.clicked.connect(self.seleccionar_carpeta)
        self.layout_controles.addWidget(self.btn_cargar)

        self.info_label = QLabel("Por favor, cargue una carpeta DICOM para comenzar.")
        self.info_label.setWordWrap(True)
        self.layout_controles.addWidget(self.info_label)
        
        # Grupo de controles DICOM (inicialmente oculto) 
        self.dicom_controls_group = QGroupBox("Controles del Visualizador")
        dicom_layout = QVBoxLayout()

        # Radio buttons para seleccionar el plano
        self.radio_axial = QRadioButton("Plano Axial")
        self.radio_coronal = QRadioButton("Plano Coronal")
        self.radio_sagital = QRadioButton("Plano Sagital")
        self.radio_axial.setChecked(True)
        self.eje_group = QButtonGroup()
        self.eje_group.addButton(self.radio_axial, 0)
        self.eje_group.addButton(self.radio_coronal, 1)
        self.eje_group.addButton(self.radio_sagital, 2)
        self.eje_group.idClicked.connect(self.actualizar_plano)
        dicom_layout.addWidget(self.radio_axial)
        dicom_layout.addWidget(self.radio_coronal)
        dicom_layout.addWidget(self.radio_sagital)
        
        # Slider para navegar por los cortes
        self.slider_label = QLabel("Corte: 0 / 0")
        dicom_layout.addWidget(self.slider_label)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.actualizar_corte)
        dicom_layout.addWidget(self.slider)

        self.dicom_controls_group.setLayout(dicom_layout)
        self.layout_controles.addWidget(self.dicom_controls_group)
        self.dicom_controls_group.setVisible(False) # Oculto hasta cargar datos

        #Panel de visualización (Derecha) 
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.ax = self.canvas.figure.subplots()
        self.ax.axis('off')
        self.ax.set_facecolor('black') # Fondo negro para la imagen

        self.layout_principal.addWidget(panel_controles)
        self.layout_principal.addWidget(self.canvas)


    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta DICOM")
        if carpeta:
            try:
                # Usamos la clase ImagenMedica del Modelo
                self.imagen_medica = ImagenMedica(carpeta, coleccion_dicom)
                self.imagen_medica.cargar_dicoms()
                self.imagen_medica.guardar_en_mongo()
                
                # Actualizar la interfaz
                self.mostrar_info_y_controles()
                self.actualizar_plano() # Muestra el primer corte axial
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar la carpeta:\n{e}")

    def mostrar_info_y_controles(self):
        metadatos = self.imagen_medica.metadatos()
        info_texto = "<b>Metadatos Principales:</b><br>"
        for clave, valor in metadatos.items():
            info_texto += f"<b>{clave}:</b> {valor}<br>"
        self.info_label.setText(info_texto)
        
        self.dicom_controls_group.setVisible(True) # Mostrar controles
        self.btn_cargar.setText("Cargar otra carpeta") # Cambiar texto del botón

    def actualizar_plano(self):
        if not self.imagen_medica: return
        
        dims = self.imagen_medica.obtener_dimensiones_volumen()
        eje_actual = self.eje_group.checkedId()
        
        # Actualizar el rango del slider según el plano seleccionado
        self.slider.setRange(0, dims[eje_actual] - 1)
        self.slider.setValue(dims[eje_actual] // 2) # Posicionar en el centro
        self.actualizar_corte() # Mostrar la imagen del corte actual

    def actualizar_corte(self):
        if not self.imagen_medica: return
        
        indice = self.slider.value()
        eje = self.eje_group.checkedId()
        
        # Obtener el corte desde el modelo
        corte_2d = self.imagen_medica.obtener_corte(eje, indice)
        
        if corte_2d is not None:
            # Actualizar el label del slider
            total_cortes = self.slider.maximum() + 1
            self.slider_label.setText(f"Corte: {indice + 1} / {total_cortes}")
            
            # Mostrar la imagen en el canvas
            self.ax.clear()
            self.ax.imshow(corte_2d, cmap='gray', aspect='auto')
            self.ax.axis('off')
            self.canvas.draw()

#EL RESTO DE TUS CLASES 
class SeñalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Señales")
        self.setGeometry(200, 200, 900, 700)

        self.layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.ax = self.canvas.figure.add_subplot(111)
        self.layout.addWidget(self.canvas)
        
        self.btn_mat = QPushButton("Abrir visualizador .mat")
        self.btn_mat.clicked.connect(self.abrir_mat_viewer)
        self.layout.addWidget(self.btn_mat)

        self.combo_llaves = QComboBox()
        self.combo_llaves.currentTextChanged.connect(self.configurar_selector_senal)
        self.layout.addWidget(QLabel("Selecciona una señal:"))
        self.layout.addWidget(self.combo_llaves)

        self.combo_ensayo = QComboBox()
        self.combo_ensayo.currentIndexChanged.connect(self.graficar_senal)
        self.combo_canal = QComboBox()
        self.combo_canal.currentIndexChanged.connect(self.graficar_senal)
        self.layout.addWidget(QLabel("Ensayo:"))
        self.layout.addWidget(self.combo_ensayo)
        self.layout.addWidget(QLabel("Canal:"))
        self.layout.addWidget(self.combo_canal)

        self.btn_csv = QPushButton("Visualizar CSV")
        self.btn_csv.clicked.connect(self.abrir_csv_view)
        self.layout.addWidget(self.btn_csv)

        self.btn_visualizador = QPushButton("Abrir visualizador interactivo (Simple)")
        self.btn_visualizador.clicked.connect(self.abrir_visualizador)
        self.layout.addWidget(self.btn_visualizador)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def abrir_csv_view(self):
        self.csv_view = CSVView()
        self.csv_view.show()

    def abrir_mat_viewer(self):
        self.mat_viewer = MatViewer()
        self.mat_viewer.show()

    def cargar_archivo_mat(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .mat", "", "Archivos MAT (*.mat)")
        if not ruta:
            return
        try:
            self.datos_mat = loadmat(ruta)
            llaves = [k for k in self.datos_mat.keys() if not k.startswith("__")]
            self.combo_llaves.clear()
            self.combo_llaves.addItems(llaves)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def configurar_selector_senal(self, llave):
        if not llave:
            return
        try:
            array = np.array(self.datos_mat[llave])
            if array.ndim != 3:
                QMessageBox.critical(self, "Error", f"La variable '{llave}' no tiene dimensiones [ensayos, muestras, canales].")
                return

            self.array_seleccionado = array
            ensayos, muestras, canales = array.shape

            self.combo_ensayo.clear()
            self.combo_ensayo.addItems([str(i) for i in range(ensayos)])
            self.combo_canal.clear()
            self.combo_canal.addItems([str(i) for i in range(canales)])

            self.graficar_senal()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al configurar señal:\n{e}")

    def graficar_senal(self):
        try:
            if self.combo_ensayo.currentText() == "" or self.combo_canal.currentText() == "":
                return 
        
            ensayo = int(self.combo_ensayo.currentText())
            canal = int(self.combo_canal.currentText())
            senal = self.array_seleccionado[ensayo, :, canal]

            self.ax.clear()
            self.ax.plot(senal, label=f"Ensayo {ensayo}, Canal {canal}")
            self.ax.set_title("Señal del archivo .mat")
            self.ax.set_xlabel("Muestras")
            self.ax.set_ylabel("Amplitud")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar la señal:\n{e}")

    def abrir_visualizador(self):
        self.visualizador = VisualizadorInteractivo()
        self.visualizador.show()

class MatViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de archivo .mat")
        self.setGeometry(300, 300, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.layout.addWidget(self.canvas)

        self.btn_cargar = QPushButton("Seleccionar archivo .mat")
        self.btn_cargar.clicked.connect(self.cargar_mat)
        self.layout.addWidget(self.btn_cargar)

        self.combo_llaves = QComboBox()
        self.combo_llaves.currentTextChanged.connect(self.configurar_selector)
        self.layout.addWidget(QLabel("Selecciona una variable:"))
        self.layout.addWidget(self.combo_llaves)

        self.combo_ensayo = QComboBox()
        self.combo_canal = QComboBox()
        self.combo_ensayo.currentIndexChanged.connect(self.graficar)
        self.combo_canal.currentIndexChanged.connect(self.graficar)

        self.layout.addWidget(QLabel("Ensayo:"))
        self.layout.addWidget(self.combo_ensayo)
        self.layout.addWidget(QLabel("Canal:"))
        self.layout.addWidget(self.combo_canal)

    def cargar_mat(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo .mat", "", "Archivos MAT (*.mat)")
        if not ruta:
            return
        try:
            self.datos_mat = loadmat(ruta)
            llaves = [k for k in self.datos_mat.keys() if not k.startswith("__")]
            self.combo_llaves.clear()
            self.combo_llaves.addItems(llaves)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def configurar_selector(self, llave):
        try:
            array = np.array(self.datos_mat[llave])
            if array.ndim != 3:
                QMessageBox.critical(self, "Error", f"La variable '{llave}' no tiene dimensiones [ensayos, muestras, canales].")
                return

            self.array = array
            ensayos, _, canales = array.shape
            self.combo_ensayo.clear()
            self.combo_ensayo.addItems([str(i) for i in range(ensayos)])
            self.combo_canal.clear()
            self.combo_canal.addItems([str(i) for i in range(canales)])
            self.graficar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al configurar la señal:\n{e}")

    def graficar(self):
        try:
            ensayo = int(self.combo_ensayo.currentText())
            canal = int(self.combo_canal.currentText())
            senal = self.array[ensayo, :, canal]

            ax = self.canvas.figure.subplots()
            ax.clear()
            ax.plot(senal, label=f"Ensayo {ensayo}, Canal {canal}")
            ax.set_title("Señal desde archivo .mat")
            ax.set_xlabel("Muestras")
            ax.set_ylabel("Amplitud")
            ax.legend()
            ax.grid(True)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar la señal:\n{e}")


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
            self.mostrar_tabla()
            self.llenar_combos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
    def mostrar_tabla(self):
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)
        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                valor = str(self.df.iat[i, j])
                self.tabla.setItem(i, j, QTableWidgetItem(valor))
    def llenar_combos(self):
        columnas = list(self.df.columns)
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_x.addItems(columnas)
        self.combo_y.addItems(columnas)
    def graficar(self):
        if self.df is None:
            QMessageBox.warning(self, "Advertencia", "Carga un archivo CSV primero.")
            return
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        try:
            x = self.df[x_col]
            y = self.df[y_col]
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.scatter(x, y)
            ax.set_title("Gráfico de Dispersión")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar:\n{e}")

class VisualizadorInteractivo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador Interactivo - GenEraVid")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.btn_imagen = QPushButton("Mostrar Imagen PNG")
        self.btn_imagen.clicked.connect(self.mostrar_imagen)
        self.btn_senal = QPushButton("Mostrar Señal")
        self.btn_senal.clicked.connect(self.mostrar_senal)
        self.btn_csv = QPushButton("Mostrar Gráfico CSV")
        self.btn_csv.clicked.connect(self.mostrar_csv)
        layout.addWidget(self.btn_imagen)
        layout.addWidget(self.btn_senal)
        layout.addWidget(self.btn_csv)
        self.setLayout(layout)
    def mostrar_imagen(self):
        ax = self.canvas.figure.subplots()
        ax.clear()
        img = cv2.imread("Cromo.png", cv2.IMREAD_GRAYSCALE)
        if img is None:
            ax.text(0.5, 0.5, "No se encontró la imagen 'Cromo.png'", ha='center')
        else:
            ax.imshow(img, cmap='gray')
            ax.set_title("Imagen PNG: Cromosomas")
        self.canvas.draw()
    def mostrar_senal(self):
        ax = self.canvas.figure.subplots()
        ax.clear()
        t = np.linspace(0, 1, 500)
        senal = np.sin(2 * np.pi * 10 * t)
        ax.plot(t, senal, label="Señal simulada")
        ax.set_title("Señal Simulada - Senoidal")
        ax.set_xlabel("Tiempo [s]")
        ax.set_ylabel("Amplitud")
        ax.legend()
        self.canvas.draw()
    def mostrar_csv(self):
        ax = self.canvas.figure.subplots()
        ax.clear()
        try:
            df = pd.read_csv("pacientes.csv") # Asegúrate que 'pacientes.csv' exista
            conteo = df["Grupo"].value_counts()
            ax.bar(conteo.index, conteo.values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_title("Distribución de Pacientes por Grupo")
            ax.set_xlabel("Grupo")
            ax.set_ylabel("Cantidad de Pacientes")
        except FileNotFoundError:
            ax.text(0.5, 0.5, "No se encontró el archivo 'pacientes.csv'", ha='center')
        except Exception as e:
            ax.text(0.5, 0.5, f"Error al leer CSV: {e}", ha='center')
        self.canvas.draw()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GenEraVid Viewer")
        self.setGeometry(150, 150, 300, 300)
        self.setStyleSheet("""
            QWidget { background: white; font-family: Arial; font-size: 14px; }
            QPushButton {background: #4da6ff; color: white; border-radius: 5px; padding: 6px;}
            QPushButton:hover { background: #3399ff; }
            QLineEdit, QComboBox { border: 1px solid lightgray; border-radius: 4px; padding: 4px;}
        """)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.mostrar_opciones_iniciales()
    def mostrar_opciones_iniciales(self):
        titulo = QLabel("Bienvenido a GenEraVid")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(titulo)
        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.clicked.connect(self.mostrar_login)
        self.layout.addWidget(self.btn_login)
        self.btn_registro = QPushButton("Registrarse")
        self.btn_registro.clicked.connect(self.mostrar_registro)
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
        # Guardamos la referencia a la nueva ventana para que no sea eliminada por el recolector de basura
        self.menu = ventana_clase()
        self.menu.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())