import math
from abc import ABC, abstractmethod


class MetodoPago(ABC):
    @abstractmethod
    def procesar_pago(self, total):
        pass


class PagoEfectivo(MetodoPago):
    def __init__(self, monto_recibido):
        self.monto_recibido = monto_recibido
        self.__total_a_cobrar = 0  
    @property
    def monto_recibido(self):
        return self.__monto_recibido

    @monto_recibido.setter
    def monto_recibido(self, monto_recibido):
        if monto_recibido < 0:
            raise ValueError("El monto recibido no puede ser negativo")
        self.__monto_recibido = monto_recibido

    def redondear_total(self, total):
        return math.floor(round(total * 2, 6)) / 2

    def procesar_pago(self, total):
        cobrado = self.redondear_total(total)
        if self.__monto_recibido < cobrado:
            raise ValueError(f"El monto recibido no cubre el total de Bs {cobrado:.2f}")
        self.__total_a_cobrar = cobrado
        return cobrado

    def calcular_cambio(self):
        return round(self.__monto_recibido - self.__total_a_cobrar, 2)


class PagoQR(MetodoPago):
    def __init__(self, codigo_transaccion):
        self.codigo_transaccion = codigo_transaccion

    @property
    def codigo_transaccion(self):
        return self.__codigo_transaccion

    @codigo_transaccion.setter
    def codigo_transaccion(self, codigo_transaccion):
        self.__codigo_transaccion = codigo_transaccion.strip()

    def validar_codigo(self):
        return len(self.__codigo_transaccion) == 10 and self.__codigo_transaccion.isdigit()

    def procesar_pago(self, total):
        if not self.validar_codigo():
            raise ValueError("El codigo de transaccion debe tener 10 digitos")
        return round(total, 2)


class PagoTarjeta(MetodoPago):
    def __init__(self, comision=0.03):
        self.comision = comision

    @property
    def comision(self):
        return self.__comision

    @comision.setter
    def comision(self, comision):
        if comision < 0 or comision >= 1:
            raise ValueError("La comision debe estar entre 0 y 1")
        self.__comision = comision

    def calcular_comision(self, total):
        return round(total * self.__comision, 2)

    def procesar_pago(self, total):
        return round(total + self.calcular_comision(total), 2)