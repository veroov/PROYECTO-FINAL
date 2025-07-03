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

class ImagenMedica:
    def __init__(self, carpeta, coleccion: Collection):
        self.carpeta = carpeta  
        self.dicoms = []
        self.volumen = None
        self.coleccion = coleccion

 #Carga todos los archivos DICOM de la carpeta
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

# Extrae metadatos del primer archivo DICOM
    def metadatos(self):
        if not self.dicoms:
            self.cargar_dicoms()
        dcm = self.dicoms[0]
        return {
            "Nombre": str(dcm.get("PatientName", "Desconocido")),
            "Edad": str(dcm.get("PatientAge", "ND")),
            "ID": str(dcm.get("PatientID", "ND")),
            "Fecha": str(dcm.get("StudyDate", "ND")),
            "Modalidad": str(dcm.get("Modality", "ND")),
        }

#Guarda metadatos y ruta en Mongo
    def guardar_en_mongo(self, ruta_nifti=None):
        datos = self.metadatos()
        datos.update({
            "carpeta_dicom": self.carpeta,
            "ruta_nifti": ruta_nifti
        })

        if not self.coleccion.find_one({"carpeta_dicom": self.carpeta}):
            self.coleccion.insert_one(datos)
            print("Datos guardados en MongoDB.")
        else:
            print("Esta carpeta ya estaba registrada.")

    def reconstruccion_volumen(self):
        """Devuelve el volumen 3D"""
        if self.volumen is None:
            self.cargar_dicoms()
        return self.volumen

