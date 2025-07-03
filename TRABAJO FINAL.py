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
