from pymongo import MongoClient
from Controlador import Usuario
from Controlador import ImagenMedica

client = MongoClient("mongodb://localhost:27017/")
db = client["Bioingenieria"]
coleccion_usuarios = db["Usuarios"]
coleccion_dicom = db["Dicom_nifti"]

username = input("Ingrese su nombre de usuario: ")
password = input("Ingrese su contraseña: ")
usuario = Usuario(username, password, None, coleccion_usuarios)
existe, rol = usuario.verificar()
if existe:
    usuario.rol = rol
    print(usuario)
else:
    print("El usuario no existe o las credenciales son incorrectas.") 


imagen = ImagenMedica("img1", coleccion_dicom)
imagen.cargar_dicoms()
print(imagen.metadatos())
imagen.guardar_en_mongo()
