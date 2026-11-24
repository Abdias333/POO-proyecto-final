from modelo.clientes import Cliente
from modelo.pagos import PagoEfectivo, PagoQR, PagoTarjeta
from modelo.pedidos import PedidoLocal, PedidoParaLlevar, PedidoDelivery
from modelo.productos import Plato, Bebida
from restaurante import Restaurante

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


def leer_entero(mensaje, minimo, maximo):
    while True:
        try:
            numero = int(input(mensaje))
            if minimo <= numero <= maximo:
                return numero
            print(f"Debe estar entre {minimo} y {maximo}")
        except ValueError:
            print("Ingrese un numero entero")


def leer_decimal(mensaje):
    while True:
        try:
            numero = float(input(mensaje).replace(",", "."))
            if numero > 0:
                return numero
            print("Debe ser mayor que cero")
        except ValueError:
            print("Ingrese un numero")


def leer_dia(mensaje):
    while True:
        dia = input(mensaje).strip().lower()
        if dia in DIAS:
            return dia
        print("Dia no valido (escriba sin tilde: lunes, martes, miercoles...)")


def elegir(lista, texto):
    # muestra una lista numerada y devuelve el elemento elegido (None = cancelar)
    if len(lista) == 0:
        print("No hay elementos registrados")
        return None
    for i, elemento in enumerate(lista, start=1):
        print(f"  {i}. {texto(elemento)}")
    print("  0. Cancelar")
    opcion = leer_entero("Elija: ", 0, len(lista))
    if opcion == 0:
        return None
    return lista[opcion - 1]


def registrar_plato(r):
    nombre = input("Nombre del plato: ")
    precio = leer_decimal("Precio (Bs): ")
    texto = input("Dias disponibles separados por coma (Enter = todos): ").strip()
    dias = DIAS if texto == "" else texto.split(",")
    r.registrar_producto(Plato(nombre, precio, dias))
    print("Plato registrado")


def registrar_bebida(r):
    nombre = input("Nombre de la bebida: ")
    precio = leer_decimal("Precio por vaso (Bs): ")
    presentacion = input("Presentacion (vaso/jarra): ")
    bebida = Bebida(f"{nombre} ({presentacion.strip().lower()})", precio, presentacion)
    r.registrar_producto(bebida)
    print(f"Bebida registrada: Bs {bebida.calcular_precio():.2f}")


def armar_combo(r):
    nombre = input("Nombre del combo: ")
    productos = []
    while True:
        print("Elija un producto para el combo (0 para terminar):")
        producto = elegir(list(r.productos), lambda p: f"{p.nombre} Bs {p.calcular_precio():.2f}")
        if producto is None:
            break
        productos.append(producto)
    combo = r.armar_combo(nombre, productos)
    print(f"Combo registrado: Bs {combo.calcular_precio():.2f}")


def registrar_cliente(r):
    nombre = input("Nombre del cliente: ")
    telefono = input("Telefono (8 digitos, empieza con 6 o 7): ")
    cliente = Cliente(nombre, telefono)
    r.registrar_cliente(cliente)
    print("Cliente registrado")
    return cliente


def nuevo_pedido(r, dia):
    print("Elija el cliente:")
    cliente = elegir(list(r.clientes), lambda c: f"{c.nombre} ({c.telefono})")
    if cliente is None:
        return
    numero = len(r.pedidos) + 1
    tipo = leer_entero("Tipo 1. Local  2. Para llevar  3. Delivery: ", 1, 3)
    if tipo == 1:
        pedido = PedidoLocal(numero, cliente, leer_entero("Numero de mesa (1 a 15): ", 1, 15))
    elif tipo == 2:
        pedido = PedidoParaLlevar(numero, cliente)
    else:
        print("Zonas: Cercado (Bs 8), Quillacollo (Bs 15), Sacaba (Bs 15), Vinto (Bs 20)")
        zona = input("Zona: ")
        direccion = input("Direccion: ")
        pedido = PedidoDelivery(numero, cliente, zona, direccion)
    r.registrar_pedido(pedido)
    print(f"Pedido #{numero} registrado")
    modificar_pedido(r, dia, pedido)


def elegir_pedido(r):
    return elegir(list(r.pedidos),
                  lambda p: f"#{p.numero} {type(p).__name__} {p.cliente.nombre} {p.estado}")


def modificar_pedido(r, dia, pedido=None):
    if pedido is None:
        pedido = elegir_pedido(r)
        if pedido is None:
            return
    while True:
        print(pedido.mostrar_detalle())
        opcion = leer_entero("1. Agregar producto  2. Quitar producto  0. Terminar: ", 0, 2)
        if opcion == 0:
            break
        try:
            if opcion == 1:
                disponibles = [p for p in r.productos if p.esta_disponible(dia)]
                producto = elegir(disponibles, lambda p: f"{p.nombre} Bs {p.calcular_precio():.2f}")
                if producto is not None:
                    pedido.agregar_producto(producto, leer_entero("Cantidad (1 a 20): ", 1, 20))
            else:
                detalle = elegir(list(pedido.detalles), lambda d: f"{d.cantidad} x {d.producto.nombre}")
                if detalle is not None:
                    pedido.quitar_producto(detalle.producto)
        except ValueError as e:
            print("Error:", e)


def cambiar_estado(r):
    pedido = elegir_pedido(r)
    if pedido is None:
        return
    print("Estado actual:", pedido.estado)
    nuevo = input("Nuevo estado (EN_PREPARACION, LISTO, ENTREGADO, CANCELADO): ")
    pedido.cambiar_estado(nuevo)
    print("Estado cambiado a", pedido.estado)


def cobrar_pedido(r):
    pedido = elegir_pedido(r)
    if pedido is None:
        return
    total = pedido.calcular_total()
    print(pedido.mostrar_detalle())
    opcion = leer_entero("Pago 1. Efectivo  2. QR  3. Tarjeta (+3 %): ", 1, 3)
    if opcion == 1:
        metodo = PagoEfectivo(0)
        print(f"Total en efectivo (redondeado a Bs 0,50): Bs {metodo.redondear_total(total):.2f}")
        metodo.monto_recibido = leer_decimal("Monto recibido (Bs): ")
    elif opcion == 2:
        metodo = PagoQR(input("Codigo de transaccion (10 digitos): "))
    else:
        metodo = PagoTarjeta()
    pedido.pagar(metodo)
    print("\n===== COMPROBANTE SABOR VALLUNO =====")
    print(pedido.mostrar_detalle())
    if opcion == 1:
        print(f"  Efectivo cobrado: Bs {metodo.redondear_total(total):.2f}")
        print(f"  Recibido: Bs {metodo.monto_recibido:.2f}  Cambio: Bs {metodo.calcular_cambio():.2f}")
    elif opcion == 2:
        print(f"  Pago QR, codigo {metodo.codigo_transaccion}: Bs {metodo.procesar_pago(total):.2f}")
    else:
        print(f"  Comision tarjeta: Bs {metodo.calcular_comision(total):.2f}")
        print(f"  Cobrado con tarjeta: Bs {metodo.procesar_pago(total):.2f}")
    print("=====================================")


def cargar_ejemplo(r):
    silpancho = Plato("Silpancho", 35, DIAS)
    pique = Plato("Pique macho", 45, DIAS)
    chicharron = Plato("Chicharron", 50, ["domingo"])
    sopa = Plato("Sopa de mani", 20, DIAS)
    mocochinchi = Bebida("Mocochinchi (vaso)", 6, "vaso")
    for p in (silpancho, pique, chicharron, sopa, mocochinchi, Bebida("Mocochinchi (jarra)", 6, "jarra")):
        r.registrar_producto(p)
    r.armar_combo("Combo Valluno", [silpancho, mocochinchi])
    print("Menu de ejemplo cargado")


def main():
    r = Restaurante()
    print("===== SABOR VALLUNO - Variante E =====")
    dia = leer_dia("Que dia es hoy? ")
    if input("Cargar menu de ejemplo? (s/n): ").strip().lower() == "s":
        cargar_ejemplo(r)
    while True:
        print(f"\n===== MENU (hoy: {dia}) =====")
        print("1. Registrar plato")
        print("2. Registrar bebida")
        print("3. Armar combo")
        print("4. Ver menu de un dia")
        print("5. Registrar cliente")
        print("6. Nuevo pedido")
        print("7. Agregar / quitar productos de un pedido")
        print("8. Ver detalle de un pedido")
        print("9. Cambiar estado o cancelar pedido")
        print("10. Cobrar pedido")
        print("11. Reporte de ventas del dia")
        print("0. Salir")
        opcion = leer_entero("Elija una opcion: ", 0, 11)
        try:
            if opcion == 0:
                print("Hasta pronto")
                break
            elif opcion == 1:
                registrar_plato(r)
            elif opcion == 2:
                registrar_bebida(r)
            elif opcion == 3:
                armar_combo(r)
            elif opcion == 4:
                r.mostrar_menu(leer_dia("Dia: "))
            elif opcion == 5:
                registrar_cliente(r)
            elif opcion == 6:
                nuevo_pedido(r, dia)
            elif opcion == 7:
                modificar_pedido(r, dia)
            elif opcion == 8:
                pedido = elegir_pedido(r)
                if pedido is not None:
                    print(pedido.mostrar_detalle())
            elif opcion == 9:
                cambiar_estado(r)
            elif opcion == 10:
                cobrar_pedido(r)
            elif opcion == 11:
                r.generar_reporte_diario()
        except ValueError as e:
            print("Error:", e)


main()