class Cliente:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, nombre):
        if nombre.strip() == "":
            raise ValueError("El nombre del cliente no puede estar vacio")
        self.__nombre = nombre.strip()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, telefono):
        self.__telefono = telefono.strip()

    def validar_telefono(self):
        t = self.__telefono
        return len(t) == 8 and t.isdigit() and (t[0] == "6" or t[0] == "7")