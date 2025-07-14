import pydicom
from datetime import datetime
import os
import numpy as np
from pymongo.collection import Collection
from pymongo import MongoClient
from scipy.io import loadmat
import pandas as pd
import cv2

#Conexión a la base de datos 
client = MongoClient("mongodb://localhost:27017/")
db = client["Bioingenieria"]
coleccion_usuarios = db["Usuarios"]
coleccion_dicom = db["Dicom_nifti"]
class Usuario:
    def __init__(self, usuario, contraseña, rol, coleccion: Collection):
        self.usuario = usuario
        self.contraseña = contraseña
        self.rol = rol
        self.coleccion = coleccion

    def guardar(self):
        if self.coleccion.find_one({"usuario": self.usuario}):
            return False, "El usuario ya existe."
        self.coleccion.insert_one({
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "rol": self.rol
        })
        return True, "Usuario registrado exitosamente."

    def verificar(self):
        usuario_encontrado = self.coleccion.find_one({
            "usuario": self.usuario,
            "contraseña": self.contraseña
        })
        if usuario_encontrado:
            return True, usuario_encontrado.get("rol", "sin rol")
        return False, "Datos incorrectos."

class ImagenMedica:
    def __init__(self, carpeta, coleccion: Collection):
        self.carpeta = carpeta
        self.coleccion = coleccion
        self.slices = []
        self.volumen = None
        self._metadatos = {}

    def cargar_dicoms(self):
        archivos = [os.path.join(self.carpeta, f) for f in os.listdir(self.carpeta) if f.endswith('.dcm')]
        if not archivos:
            raise ValueError("No se encontraron archivos DICOM (.dcm) en la carpeta.")
        self.slices = [pydicom.dcmread(f) for f in archivos]
        self.slices.sort(key=lambda x: int(x.InstanceNumber))
        self.volumen = np.stack([s.pixel_array for s in self.slices])
        primer_slice = self.slices[0]
        self._metadatos = {
            "ID del Paciente": primer_slice.PatientID,
            "Modalidad": primer_slice.Modality,
            "Dimensiones": f"{primer_slice.Rows}x{primer_slice.Columns}",
            "Número de Slices": len(self.slices)
        }
        return True

    def guardar_en_mongo(self):
        if not self._metadatos:
            print("No hay metadatos para guardar. Carga los DICOMs primero.")
            return

        datos_a_guardar = self._metadatos.copy()
        datos_a_guardar['ruta_carpeta'] = self.carpeta
        
        if not self.coleccion.find_one({"ruta_carpeta": self.carpeta}):
            self.coleccion.insert_one(datos_a_guardar)
            print("Metadatos guardados en MongoDB.")
        else:
            print("Los metadatos para esta carpeta ya existen en MongoDB.")

    def metadatos(self):
        return self._metadatos

    def obtener_dimensiones_volumen(self):
        #"""Devuelve las dimensiones del volumen (slices, filas, columnas)."""
        return self.volumen.shape if self.volumen is not None else (0, 0, 0)

    def obtener_corte(self, eje, indice):
        #"""
       # Obtiene un corte 2D del volumen.
        #eje 0: Axial (corte a lo largo de los slices)
        #eje 1: Coronal (corte a lo largo de las filas)
       # eje 2: Sagital (corte a lo largo de las columnas)
        #"""
        if self.volumen is None:
            return None
        
        max_indice = self.volumen.shape[eje] - 1
        indice = max(0, min(indice, max_indice))

        if eje == 0:  # Plano Axial
            return self.volumen[indice, :, :]
        elif eje == 1:  # Plano Coronal
            return self.volumen[:, indice, :]
        elif eje == 2:  # Plano Sagital
            return self.volumen[:, :, indice]
        return None
class ProcesadorImagen:
    def __init__(self, ruta):
        self.ruta = ruta
        self.original = cv2.imread(ruta, cv2.IMREAD_COLOR)
        self.procesada = self.original.copy()

    def cambiar_espacio_color(self, modo="gris"):
        if modo == "gris":
            self.procesada = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        elif modo == "hsv":
            self.procesada = cv2.cvtColor(self.original, cv2.COLOR_BGR2HSV)
        return self.procesada

    def ecualizar(self):
        gris = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.procesada = cv2.equalizeHist(gris)
        return self.procesada

    def binarizar(self, umbral=127):
        gris = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        _, self.procesada = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
        return self.procesada

    def operacion_morfologica(self, tipo="apertura", tam_kernel=5):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (tam_kernel, tam_kernel))
        binaria = self.binarizar()
        if tipo == "apertura":
            self.procesada = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel)
        elif tipo == "cierre":
            self.procesada = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, kernel)
        return self.procesada

    def contar_celulas(self):
        gris = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        _, binaria = cv2.threshold(gris, 127, 255, cv2.THRESH_BINARY_INV)
        contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len(contornos)
    def invertir_imagen(self): # método no visto en clase  de opencv
        self.procesada = cv2.bitwise_not(self.original)
        return self.procesada
        
class GestorSeñales:
    def __init__(self):
        self.datos_mat = {}

    def cargar_mat(self, ruta):
        """Carga un archivo .mat y devuelve las llaves disponibles."""
        self.datos_mat = loadmat(ruta)
        return [k for k in self.datos_mat.keys() if not k.startswith("__")]

    def obtener_senal(self, llave):
        """Devuelve el array de la señal correspondiente a la llave seleccionada."""
        if llave in self.datos_mat:
            return np.squeeze(self.datos_mat[llave])
        return None

class GestorCSV:
    def __init__(self):
        self.df = None

    def cargar_csv(self, ruta):
        try:
            self.df = pd.read_csv(ruta)
            return self.df
        except Exception as e:
            print(f"Error al cargar CSV: {e}")
            return None

    def obtener_columnas(self):
        """Devuelve la lista de nombres de columnas del DataFrame."""
        if self.df is not None:
            return list(self.df.columns)
        return []

    def obtener_datos(self):
        """Devuelve el DataFrame completo."""
        return self.df

    def obtener_datos_columnas(self, col_x, col_y):
        """Devuelve los datos de dos columnas específicas."""
        if self.df is not None and col_x in self.df.columns and col_y in self.df.columns:
            return self.df[col_x], self.df[col_y]
        return None, None

class RegistroArchivo:
    def __init__(self, tipo, nombre_archivo, ruta, coleccion):
        self.tipo = tipo  # Ej: "csv", "mat", "jpg"
        self.nombre_archivo = nombre_archivo
        self.ruta = ruta
        self.fecha = datetime.now()
        self.coleccion = coleccion

    def guardar(self):
        doc = {
            "codigo": self.generar_codigo(),
            "tipo": self.tipo,
            "nombre_archivo": self.nombre_archivo,
            "fecha": self.fecha,
            "ruta": self.ruta
        }
        self.coleccion.insert_one(doc)

    def generar_codigo(self):
        # Código simple tipo: CSV-00001, MAT-00002, etc.
        prefijo = self.tipo.upper()
        total = self.coleccion.count_documents({"tipo": self.tipo}) + 1
        return f"{prefijo}-{total:05d}"
