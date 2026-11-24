from datetime import date

from modelo.pedidos import PedidoLocal
from modelo.productos import Combo


class Restaurante:
    def __init__(self):
        self.__productos = []
        self.__clientes = []
        self.__pedidos = []

    @property
    def productos(self):
        return tuple(self.__productos)

    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def pedidos(self):
        return tuple(self.__pedidos)

    def registrar_producto(self, p):
        self.__productos.append(p)

    def armar_combo(self, nombre, productos):
        if len(productos) < 2:
            raise ValueError("Un combo debe tener 2 o mas productos")
        combo = Combo(nombre)
        for producto in productos:
            combo.agregar_componente(producto, 1)
        self.registrar_producto(combo)
        return combo

    def registrar_cliente(self, c):
        if not c.validar_telefono():
            raise ValueError("Telefono invalido: 8 digitos y empieza con 6 o 7")
        self.__clientes.append(c)

    def registrar_pedido(self, pedido):
        if isinstance(pedido, PedidoLocal):
            for otro in self.__pedidos:
                if (isinstance(otro, PedidoLocal) and otro.numero_mesa == pedido.numero_mesa
                        and otro.estado not in ("ENTREGADO", "CANCELADO")):
                    raise ValueError(f"La mesa {pedido.numero_mesa} ya tiene un pedido abierto")
        self.__pedidos.append(pedido)

    def mostrar_menu(self, dia):
        print(f"\n--- Menu del {dia} ---")
        for p in self.__productos:
            if p.esta_disponible(dia):
                print(f"  {p.nombre}: Bs {p.calcular_precio():.2f}")

    def generar_reporte_diario(self):
        hoy = date.today()
        print(f"\n=== Reporte de ventas {hoy} ===")
        por_tipo = {}
        for p in self.__pedidos:
            if p.fecha_registro.date() == hoy and p.estado != "CANCELADO":
                tipo = type(p).__name__
                if tipo not in por_tipo:
                    por_tipo[tipo] = [0, 0]
                por_tipo[tipo][0] += 1
                por_tipo[tipo][1] += p.calcular_total()
        total = 0
        for tipo, datos in por_tipo.items():
            print(f"  {tipo}: {datos[0]} pedidos, Bs {datos[1]:.2f}")
            total += datos[1]
        print(f"  Total del dia: Bs {total:.2f}")
        print("Top 3 productos:")
        for nombre, cantidad in self.obtener_top_3_productos():
            print(f"  {nombre}: {cantidad}")

    def obtener_top_3_productos(self):
        conteo = {}
        for pedido in self.__pedidos:
            if pedido.estado != "CANCELADO":
                for d in pedido.detalles:
                    conteo[d.producto.nombre] = conteo.get(d.producto.nombre, 0) + d.cantidad
        ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        return ordenado[:3]