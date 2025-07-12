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
class GestorImagenesMedicas:
    def cargar_dicom(self, carpeta):
        pass

    def convertir_a_nifti(self, carpeta_dicom, salida):
        pass

    def extraer_metadatos(self, dicom_path):
        pass

    def reconstruir_3d(self):
        pass

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
