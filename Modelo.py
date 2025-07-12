import pandas as pd
import os
import numpy as np
import pydicom
from pymongo.collection import Collection

class Usuario:
    def __init__(self, usuario, contraseña, rol, coleccion):  
        self.usuario = usuario
        self.contraseña = contraseña
        self.rol = rol 
        self.coleccion = coleccion

    # Guarda un nuevo usuario en MongoDB si no existe
    def guardar(self):
        if self.coleccion.find_one({"usuario": self.usuario}):
            return False, "El usuario ya existe."
        if self.rol == "imagenes":
            nombre = f"Usuario imágenes - {self.usuario}"
        elif self.rol == "señales":
            nombre = f"Usuario señales - {self.usuario}"
        else:
            nombre = self.usuario 

        self.coleccion.insert_one({
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "rol": self.rol
        })
        return True, "Usuario registrado exitosamente."

    # Verifica las credenciales del usuario
    def verificar(self):
        usuario = self.coleccion.find_one({
            "usuario": self.usuario,
            "contraseña": self.contraseña
        })
        if usuario:
            return True, usuario["rol"]
        return False, "datos incorrectos."
    
    def __str__(self):
        return f"bienvenido usuario {self.usuario}, usted es experto en {self.rol}"
class GestorBaseDatos:
    def __init__(self, tipo="sql"):
        pass  # conecta con MongoDB o SQLite

    def verificar_usuario(self, username, password):
        pass

    def registrar_usuario(self, datos_usuario):
        pass

    def guardar_archivo(self, tipo_archivo, ruta, metadatos):
        pass

    def obtener_datos_usuario(self, username):
        pass
#######
class ImagenMedica:
    def __init__(self, carpeta, coleccion: Collection):
        self.carpeta = carpeta  
        self.dicoms = []
        self.volumen = None
        self.coleccion = coleccion

    def cargar_dicoms(self):
        archivos = sorted(os.listdir(self.carpeta))
        imagenes = []

        for archivo in archivos:
            ruta = os.path.join(self.carpeta, archivo)
            try:
                dcm = pydicom.dcmread(ruta)
                self.dicoms.append(dcm)
                imagenes.append(dcm.pixel_array)
            except Exception:
                print(f"No se pudo leer: {ruta}")
        
        self.volumen = np.array(imagenes)
        print(f"Volumen cargado con forma: {self.volumen.shape}")

    def convertir_a_nifti(self, carpeta_dicom, salida):
        pass

    def metadatos(self):
        if not self.dicoms:
            self.cargar_dicoms()
        dcm = self.dicoms[0]
        return { "Nombre": str(dcm.get("PatientName", "Desconocido")),
            "Edad": str(dcm.get("PatientAge", "ND")),
            "ID": str(dcm.get("PatientID", "ND")),
            "Fecha": str(dcm.get("StudyDate", "ND")),
            "Modalidad": str(dcm.get("Modality", "ND")), }
    
    def guardar_en_mongo(self, ruta_nifti=None):
        datos = self.metadatos()
        datos.update({ "carpeta_dicom": self.carpeta,
            "ruta_nifti": ruta_nifti})

        if not self.coleccion.find_one({"carpeta_dicom": self.carpeta}):
            self.coleccion.insert_one(datos)
            print("Datos guardados en MongoDB.")
        else:
            print("Esta carpeta ya estaba registrada.")

    def reconstruccion_volumen(self):
        if self.volumen is None:
            self.cargar_dicoms()
        return self.volumen

    def obtener_corte(self, eje, indice):
        pass
#####
class GestorSenales:
    def cargar_archivo_mat(self, ruta):
        pass

    def obtener_llaves(self):
        pass

    def extraer_array(self, llave):
        pass

    def graficar_intervalo(self, canal, inicio, fin):
        pass

    def calcular_promedio_eje1(self):
        pass
#####
class GestorCSV:
  def __init__(self):
        self.csv = None

def cargar_csv(self, ruta):
        self.csv = pd.read_csv(ruta)
        return self.csv

def obtener_columnas(self):
        return list(self.csv.columns) if self.csv is not None else []

def obtener_datos(self):
        return self.csv

def graficar_dispersion(self, col_x, col_y, plt):
        if self.csv is not None:
            plt.scatter(self.df[col_x], self.df[col_y])
            plt.xlabel(col_x)
            plt.ylabel(col_y)
            plt.title("Gráfico de dispersión")
            plt.grid(True)

      
#####
