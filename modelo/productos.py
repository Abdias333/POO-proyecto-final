from abc import ABC, abstractmethod


class Producto(ABC):
    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        if nombre.strip() == "":
            raise ValueError("El nombre del producto no puede estar vacio")
        self._nombre = nombre.strip()

    @property
    def precio_base(self):
        return self._precio_base

    @precio_base.setter
    def precio_base(self, precio_base):
        if precio_base <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        self._precio_base = precio_base

    @abstractmethod
    def calcular_precio(self):
        pass

    @abstractmethod
    def esta_disponible(self, dia):
        pass

    @abstractmethod
    def contar_platos(self):
        pass


class Plato(Producto):
    def __init__(self, nombre, precio_base, dias_disponibles):
        super().__init__(nombre, precio_base)
        self.dias_disponibles = dias_disponibles

    @property
    def dias_disponibles(self):
        return tuple(self.__dias_disponibles)

    @dias_disponibles.setter
    def dias_disponibles(self, dias_disponibles):
        if len(dias_disponibles) == 0:
            raise ValueError("El plato debe tener al menos un dia disponible")
        self.__dias_disponibles = [dia.strip().lower() for dia in dias_disponibles]

    def calcular_precio(self):
        return round(self._precio_base, 2)

    def esta_disponible(self, dia):
        return dia.strip().lower() in self.__dias_disponibles

    def contar_platos(self):
        return 1


class Bebida(Producto):
    # precio_base = precio por vaso. La jarra cuesta 3 veces el vaso.
    def __init__(self, nombre, precio_base, presentacion):
        super().__init__(nombre, precio_base)
        self.presentacion = presentacion

    @property
    def presentacion(self):
        return self.__presentacion

    @presentacion.setter
    def presentacion(self, presentacion):
        presentacion = presentacion.strip().lower()
        if presentacion == "vaso" or presentacion == "jarra":
            self.__presentacion = presentacion
        else:
            raise ValueError("La presentacion debe ser vaso o jarra")

    def calcular_precio(self):
        if self.__presentacion == "jarra":
            return round(self._precio_base * 3, 2)
        return round(self._precio_base, 2)

    def esta_disponible(self, dia):
        return True

    def contar_platos(self):
        return 0  # las bebidas no pagan envase


class ComponenteCombo:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad

    @property
    def producto(self):
        return self.__producto

    @producto.setter
    def producto(self, producto):
        self.__producto = producto

    @property
    def cantidad(self):
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, cantidad):
        if cantidad < 1:
            raise ValueError("La cantidad del componente debe ser al menos 1")
        self.__cantidad = cantidad

    def calcular_subtotal(self):
        return round(self.__producto.calcular_precio() * self.__cantidad, 2)

    def esta_disponible(self, dia):
        return self.__producto.esta_disponible(dia)

    def contar_platos(self):
        return self.__producto.contar_platos() * self.__cantidad


class Combo(Producto):
    # Variante E: 10 % de descuento
    def __init__(self, nombre, descuento=0.10):
        self.__componentes = []
        self.descuento = descuento
        super().__init__(nombre, 1)  # precio_base se actualiza al agregar componentes

    @property
    def componentes(self):
        return tuple(self.__componentes)

    @property
    def descuento(self):
        return self.__descuento

    @descuento.setter
    def descuento(self, descuento):
        if descuento < 0 or descuento >= 1:
            raise ValueError("El descuento debe estar entre 0 y 1")
        self.__descuento = descuento

    def agregar_componente(self, producto, cantidad):
        if producto is self:
            raise ValueError("Un combo no puede contenerse a si mismo")
        for componente in self.__componentes:
            if componente.producto is producto:
                componente.cantidad = componente.cantidad + cantidad
                break
        else:
            self.__componentes.append(ComponenteCombo(producto, cantidad))
        # precio_base = suma de sus productos sin descuento
        self._precio_base = sum(c.calcular_subtotal() for c in self.__componentes)

    def calcular_precio(self):
        # cada componente calcula su precio, aunque sea otro combo
        suma = sum(c.calcular_subtotal() for c in self.__componentes)
        return round(suma * (1 - self.__descuento), 2)

    def esta_disponible(self, dia):
        return all(c.esta_disponible(dia) for c in self.__componentes)

    def contar_platos(self):
        return sum(c.contar_platos() for c in self.__componentes)