from abc import ABC, abstractmethod
from datetime import datetime

from modelo.pagos import PagoTarjeta


class DetallePedido:
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
        if cantidad < 1 or cantidad > 20:
            raise ValueError("La cantidad debe estar entre 1 y 20")
        self.__cantidad = cantidad

    def calcular_subtotal(self):
        return round(self.__producto.calcular_precio() * self.__cantidad, 2)

    def contar_platos(self):
        return self.__producto.contar_platos() * self.__cantidad


class Pedido(ABC):
    def __init__(self, numero, cliente):
        self._numero = numero
        self._cliente = cliente
        self._detalles = []
        self._estado = "REGISTRADO"
        self._fecha_registro = datetime.now()
        self._metodo_pago = None

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def detalles(self):
        return tuple(self._detalles) 
    @property
    def estado(self):
        return self._estado

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @property
    def metodo_pago(self):
        return self._metodo_pago

    def agregar_producto(self, producto, cantidad):
        if self._estado != "REGISTRADO":
            raise ValueError("Solo se agregan productos en estado REGISTRADO")
        for detalle in self._detalles:
            if detalle.producto is producto:
                detalle.cantidad = detalle.cantidad + cantidad
                return
        self._detalles.append(DetallePedido(producto, cantidad))

    def quitar_producto(self, producto):
        if self._estado != "REGISTRADO":
            raise ValueError("Solo se quitan productos en estado REGISTRADO")
        for detalle in self._detalles:
            if detalle.producto is producto:
                self._detalles.remove(detalle)
                return
        raise ValueError("Ese producto no esta en el pedido")

    def calcular_subtotal(self):
        return round(sum(d.calcular_subtotal() for d in self._detalles), 2)

    def contar_platos(self):
        return sum(d.contar_platos() for d in self._detalles)

    @abstractmethod
    def calcular_cargos(self):
        pass

    def calcular_total(self):
        return round(self.calcular_subtotal() + self.calcular_cargos(), 2)

    def cambiar_estado(self, nuevo):
        
        siguiente = {"REGISTRADO": "EN_PREPARACION",
                     "EN_PREPARACION": "LISTO",
                     "LISTO": "ENTREGADO"}
        nuevo = nuevo.strip().upper()
        if nuevo == "CANCELADO" and self._estado == "REGISTRADO":
            self._estado = nuevo
        elif siguiente.get(self._estado) == nuevo:
            self._estado = nuevo
        else:
            raise ValueError(f"Cambio de estado no permitido: {self._estado} -> {nuevo}")

    def cancelar(self):
        self.cambiar_estado("CANCELADO")

    def pagar(self, metodo):
        if self._estado == "CANCELADO":
            raise ValueError("No se puede cobrar un pedido cancelado")
        if self._metodo_pago is not None:
            raise ValueError("El pedido ya fue pagado")
        if len(self._detalles) == 0:
            raise ValueError("El pedido no tiene productos")
        metodo.procesar_pago(self.calcular_total())
        self._metodo_pago = metodo

    def mostrar_detalle(self):
        texto = f"Pedido #{self._numero} - Cliente: {self._cliente.nombre} - Estado: {self._estado}\n"
        for d in self._detalles:
            texto += f"  {d.cantidad} x {d.producto.nombre}: Bs {d.calcular_subtotal():.2f}\n"
        texto += f"  Subtotal: Bs {self.calcular_subtotal():.2f}\n"
        texto += f"  Cargos:   Bs {self.calcular_cargos():.2f}\n"
        texto += f"  Total:    Bs {self.calcular_total():.2f}"
        return texto


class PedidoLocal(Pedido):
    def __init__(self, numero, cliente, numero_mesa):
        super().__init__(numero, cliente)
        self.numero_mesa = numero_mesa

    @property
    def numero_mesa(self):
        return self.__numero_mesa

    @numero_mesa.setter
    def numero_mesa(self, numero_mesa):
        if numero_mesa < 1 or numero_mesa > 15:
            raise ValueError("La mesa debe estar entre 1 y 15")
        self.__numero_mesa = numero_mesa

    def calcular_cargos(self):
        return 0


class PedidoParaLlevar(Pedido):
    
    def __init__(self, numero, cliente, costo_envase=3):
        super().__init__(numero, cliente)
        self.__costo_envase = costo_envase

    @property
    def costo_envase(self):
        return self.__costo_envase

    def calcular_cargos(self):
        
        return round(self.__costo_envase * self.contar_platos(), 2)


class PedidoDelivery(Pedido):
    
    def __init__(self, numero, cliente, zona, direccion, pedido_minimo=45):
        super().__init__(numero, cliente)
        self.zona = zona
        self.direccion = direccion
        self.__pedido_minimo = pedido_minimo

    @property
    def zona(self):
        return self.__zona

    @zona.setter
    def zona(self, zona):
        zona = zona.strip().capitalize()
        if zona not in ("Cercado", "Quillacollo", "Sacaba", "Vinto"):
            raise ValueError("Zona no valida")
        self.__zona = zona

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, direccion):
        if direccion.strip() == "":
            raise ValueError("La direccion no puede estar vacia")
        self.__direccion = direccion.strip()

    @property
    def pedido_minimo(self):
        return self.__pedido_minimo

    def calcular_cargos(self):
        
        if self.__zona == "Cercado" and self.calcular_subtotal() >= 180:
            return 0
        tarifas = {"Cercado": 8, "Quillacollo": 15, "Sacaba": 15, "Vinto": 20}
        return tarifas[self.__zona]

    def validar_pedido_minimo(self):
        return self.calcular_subtotal() >= self.__pedido_minimo

    def pagar(self, metodo):
        if isinstance(metodo, PagoTarjeta):
            raise ValueError("El delivery solo acepta efectivo o QR")
        if not self.validar_pedido_minimo():
            raise ValueError(f"El pedido minimo de delivery es Bs {self.__pedido_minimo}")
        super().pagar(metodo)