import pydicom
import os
import numpy as np
from pymongo.collection import Collection
from pymongo import MongoClient

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
        """Devuelve las dimensiones del volumen (slices, filas, columnas)."""
        return self.volumen.shape if self.volumen is not None else (0, 0, 0)

    def obtener_corte(self, eje, indice):
        """
        Obtiene un corte 2D del volumen.
        eje 0: Axial (corte a lo largo de los slices)
        eje 1: Coronal (corte a lo largo de las filas)
        eje 2: Sagital (corte a lo largo de las columnas)
        """
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