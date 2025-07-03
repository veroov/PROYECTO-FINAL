from pymongo import MongoClient
from Trabajo_final import Usuario

client = MongoClient("mongodb://localhost:27017/")
db = client["Base-trabajo"]
coleccion_usuarios = db["Usuarios"]

username = input("Ingrese su nombre de usuario: ")
password = input("Ingrese su contraseña: ")
usuario = Usuario(username, password, None, coleccion_usuarios)
existe, rol = usuario.verificar()
if existe:
    usuario.rol = rol
    print(usuario)
else:
    print("El usuario no existe o las credenciales son incorrectas.")
