import sys
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QSlider, QRadioButton, QButtonGroup, QGroupBox, QStackedWidget
)
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.io import loadmat
import cv2
from Modelo import coleccion_usuarios, coleccion_dicom
from Modelo import ProcesadorImagen, GestorSeñales, GestorCSV  

#Clase ImagenMenu 
class ImagenMenu(QMainWindow):
    def __init__(self):
        # super().__init__() es un comando esencial que ejecuta el constructor de la clase padre (QMainWindow),
        # asegurando que nuestra ventana se inicialice correctamente.
        super().__init__()
        self.setWindowTitle("Menú - Visualizador de Imágenes DICOM")
        self.setGeometry(100, 100, 800, 600)
        
        self.imagen_medica = None # Objeto para manejar la lógica DICOM

        #Layout principal
        main_widget = QWidget()
        # setCentralWidget() establece el widget principal sobre el cual se construirán los demás layouts.
        self.setCentralWidget(main_widget)
        self.layout_principal = QHBoxLayout(main_widget)

        #Panel de controles (Izquierda) 
        panel_controles = QWidget()
        panel_controles.setFixedWidth(250)
        self.layout_controles = QVBoxLayout(panel_controles)
        self.layout_controles.setAlignment(Qt.AlignTop)

        self.btn_cargar = QPushButton("Seleccionar Carpeta DICOM")
        # .clicked.connect() es el mecanismo de "señales y slots" de PyQt5, fundamental para la interactividad.
        # Conecta la señal "clicked" del botón con el "slot" (la función) 'seleccionar_carpeta'.
        self.btn_cargar.clicked.connect(self.seleccionar_carpeta)
        # .addWidget() es el comando para añadir un componente (como un botón) a un layout.
        self.layout_controles.addWidget(self.btn_cargar)

        self.btn_procesar = QPushButton("Procesar imagen JPG/PNG")
        self.btn_procesar.clicked.connect(self.procesar_imagen)
        self.layout_controles.addWidget(self.btn_procesar)

        self.info_label = QLabel("")
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
        
        #Se agrega  para elegir el proceso a realizar
        self.combo_accion = QComboBox()
        self.combo_accion.addItems([
            "gris",
            "hsv",
            "ecualizar",
            "binarizar",
            "apertura",
            "cierre",
            "invertir",
            "contar"
        ])
        self.layout_controles.addWidget(QLabel("Selecciona acción:"))
        self.layout_controles.addWidget(self.combo_accion)


    def setControlador(self,c):
        self.coordinador = c



    def seleccionar_carpeta(self):
        # QFileDialog.getExistingDirectory abre un diálogo nativo del sistema para que el usuario elija una carpeta.
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta DICOM")
        if carpeta:
            try:
                self.carpeta_actual = carpeta
                self.coordinador.seleccionar_archivo(carpeta)
                self.coordinador.guardar_paciente(carpeta)
                self.mostrar_info_y_controles()  # Activar los controles
                QMessageBox.information(self, "Éxito", "Carpeta DICOM cargada correctamente.")

            except Exception as e:
                # QMessageBox.critical muestra una ventana emergente de error para informar al usuario.
                QMessageBox.critical(self, "Error", f"No se pudo cargar la carpeta:\n{e}")

    def mostrar_info_y_controles(self): 
        metadatos = self.coordinador.metadatos_dicom(self.carpeta_actual)
        info_texto = "<b>Metadatos Principales:</b><br>"
        for clave, valor in metadatos.items():
            info_texto += f"<b>{clave}:</b> {valor}<br>"
        self.info_label.setText(info_texto)
        
        self.dicom_controls_group.setVisible(True) # Mostrar controles
        self.btn_cargar.setText("Cargar otra carpeta") # Cambiar texto del botón

    def actualizar_plano(self):
        eje_actual = self.eje_group.checkedId()
        dims = self.coordinador.obtener_dimensiones(self.carpeta_actual)

        # Actualizar el rango del slider según el plano seleccionado
        self.slider.setRange(0, dims[eje_actual] - 1)
        self.slider.setValue(dims[eje_actual] // 2) # Posicionar en el centro
        self.actualizar_corte()

    def actualizar_corte(self): 
        indice = self.slider.value()
        eje = self.eje_group.checkedId()
        
        # Obtener el corte desde el modelo
        corte_2d = self.coordinador.obtener_corte( eje, indice, self.carpeta_actual)

        if corte_2d is not None:
            # Actualizar el label del slider
            total_cortes = self.slider.maximum() + 1
            self.slider_label.setText(f"Corte: {indice + 1} / {total_cortes}")
            
            # Mostrar la imagen en el canvas
            # ax.clear() es un comando vital: borra el contenido anterior del gráfico antes de dibujar uno nuevo.
            self.ax.clear()
             # ax.imshow() es la función de Matplotlib para renderizar un array 2D (una matriz) como una imagen.
            self.ax.imshow(corte_2d, cmap='gray', aspect='auto')
            self.ax.axis('off')
            # canvas.draw() actualiza el lienzo, haciendo que el nuevo gráfico sea visible en la interfaz.
            self.canvas.draw()

    def procesar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if not ruta:
            return

        try:
            # Crear procesador
            procesador = ProcesadorImagen(ruta)

            # Aplicar transformación (puedes ir cambiando esto según la funcionalidad que quieras mostrar)
            img_procesada = procesador.operacion_morfologica(tipo="cierre", tam_kernel=5)

            # Mostrar en el canvas
            self.ax.clear()
            if len(img_procesada.shape) == 2:  # blanco y negro
                self.ax.imshow(img_procesada, cmap='gray')
            else:
                self.ax.imshow(cv2.cvtColor(img_procesada, cv2.COLOR_BGR2RGB))
            self.ax.set_title("Imagen Procesada")
            self.ax.axis('off')
            self.canvas.draw()

            # Opcional: Mostrar número de células
            conteo = procesador.contar_celulas()
            QMessageBox.information(self, "Conteo de Células", f"Se detectaron {conteo} células.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar la imagen:\n{e}")



class SeñalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú - Señales")
        self.setGeometry(200, 200, 900, 700)

        self.layout = QVBoxLayout()
        
        self.btn_mat = QPushButton("Abrir visualizador .mat")
        self.btn_mat.clicked.connect(self.abrir_mat_viewer)
        self.layout.addWidget(self.btn_mat)

        self.btn_csv = QPushButton("Visualizar CSV")
        self.btn_csv.clicked.connect(self.abrir_csv_view)
        self.layout.addWidget(self.btn_csv)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def abrir_csv_view(self):
        self.csv_view = CSVView()
        self.csv_view.setControlador(self.coordinador) # se conecta el menu de señales con el coordinador 
        self.csv_view.show()

    def abrir_mat_viewer(self):
        self.mat_viewer = MatViewer()
        self.mat_viewer.show()

class MatViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de archivo .mat")
        self.setGeometry(300, 300, 800, 600)
         # Botón para calcular y graficar promedio tipo stem
        self.btn_promedio = QPushButton("Calcular Promedio y Graficar Stem")
        self.btn_promedio.clicked.connect(self.graficar_promedio_stem)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.gestor = GestorSeñales()
        self.array = None

        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.ax = self.canvas.figure.add_subplot(111)
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
            # loadmat() lee el archivo .mat y lo carga como un diccionario de Python, donde las llaves
            # son los nombres de las variables y los valores son los arrays de NumPy.
            llaves = self.gestor.cargar_mat(ruta)
            self.combo_llaves.clear()
            self.combo_llaves.addItems(llaves)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def configurar_selector(self, llave):
        try:
            array = self.gestor.obtener_senal(llave)
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
            if not self.combo_ensayo.currentText().isdigit() or not self.combo_canal.currentText().isdigit():
                return
        
            ensayo = int(self.combo_ensayo.currentText())
            canal = int(self.combo_canal.currentText())
            senal = self.array[ensayo, :, canal]

            self.ax.clear()  # Limpia el gráfico anterior
            self.ax.plot(senal, label=f"Ensayo {ensayo}, Canal {canal}")
            self.ax.set_title("Señal desde archivo .mat")
            self.ax.set_xlabel("Muestras")
            self.ax.set_ylabel("Amplitud")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar la señal:\n{e}")
        #Clasificar promedio 
    def graficar_promedio_stem(self):
        if self.array is None:
            QMessageBox.warning(self, "Advertencia", "Primero debes cargar una señal válida.")
            return
        try:
        # Calcular el promedio sobre el eje 1 (muestras)
            promedio = np.mean(self.array, axis=1).mean(axis=0)  # (ensayos, muestras, canales) → promedio por canal

            self.ax.clear()
            self.ax.stem(promedio)
            self.ax.set_title("Promedio por Canal (Gráfico Stem)")
            self.ax.set_xlabel("Canal")
            self.ax.set_ylabel("Amplitud Promedio")
            self.ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar el promedio:\n{e}")


class CSVView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Viewer")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.gestor_csv = GestorCSV()
        
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
        
    def cargar_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV", "", "CSV Files (*.csv)")
        if not ruta:
            return
        try:
            # pd.read_csv() es el comando principal de Pandas para leer un archivo CSV.
            # Automáticamente lo convierte en un DataFrame, una estructura de tabla optimizada. 
            self.gestor_csv = self.coordinador.cargar_csv(ruta)
            self.coordinador.registrar_csv(ruta)

            df = self.gestor_csv.obtener_datos()
            if df is not None:
                self.mostrar_tabla()
                self.llenar_combos()

        except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def mostrar_tabla(self,df):
        
        if df is None:
            return
        
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j in range(len(df.columns)):
                valor = str(df.iat[i, j])
                self.tabla.setItem(i, j, QTableWidgetItem(valor))

    def llenar_combos(self):
        columnas = self.gestor_csv.obtener_columnas()
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_x.addItems(columnas)
        self.combo_y.addItems(columnas)

    def graficar(self):
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        
        x, y = self.coordinador.obtener_datos_columnas(self.gestor_csv, x_col, y_col)
        if x is None or y is None:
            QMessageBox.warning(self, "Advertencia", "Datos inválidos para graficar.")
            return
        try: 
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            # ax.scatter() es la función de Matplotlib usada para crear un gráfico de dispersión (scatter plot).
            ax.scatter(x, y)
            ax.set_title("Gráfico de Dispersión")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo graficar:\n{e}")

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

    def asignarCoordinador(self,c):
        self.controlador = c

    def verificar_login(self):
        username = self.input_usuario.text().strip() 
        password = self.input_contra.text().strip()
        valido, rol = self.controlador.verificar_login(username, password) #verifica credenciales y lo manda al controlador
        if valido: #si es valido va a asiganarle un rol
            rol = rol.strip().lower()
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
        if hasattr(self.menu, "setControlador"):
            self.menu.setControlador(self.controlador)
        self.menu.show()

