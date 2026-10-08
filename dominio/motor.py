"""Motor de transferencias: orquesta las estructuras dinámicas.

Flujo de una transferencia
  1. recibir()  -> se encola en la cola principal (FIFO) y se indexa en el AVL.
  2. procesar_siguiente() -> se desencola y se consulta al switch:
       - aprobada            -> pila de reversiones + historial
       - falla temporal      -> cola de reintentos (máx. 3 intentos)
       - fondos insuficientes o 3 fallas -> rechazo + notificación al cliente
  3. revertir_ultima() -> se desapila la última aprobada (LIFO).
Ninguna rama descarta una transferencia sin dejar rastro.
"""
import random
from datetime import datetime

from estructuras import ArbolAVL, ColaEnlazada, ListaDobleEnlazada, PilaEnlazada
from .cola_legado import ColaArregloEstatico
from .switch_simulado import Respuesta, SwitchSimulado
from .transferencia import CANALES, Estado, Evento, Transferencia

MAX_INTENTOS = 3
ID_INICIAL = 100001


def _normalizar_cuenta(texto):
    digitos = "".join(c for c in str(texto) if c.isdigit())
    if len(digitos) != 13:
        raise ValueError("La cuenta debe tener 13 dígitos")
    return digitos


class MotorTransferencias:
    def __init__(self, switch=None, semilla=None, capacidad_legado=5000):
        self.cola_principal = ColaEnlazada()
        self.cola_reintentos = ColaEnlazada()
        self.pila_reversiones = PilaEnlazada()
        self.historial = ListaDobleEnlazada()
        self.indice = ArbolAVL()
        self.notificaciones = ColaEnlazada()   # mensajes pendientes para la interfaz
        self.switch = switch or SwitchSimulado(semilla=semilla)
        self.legado = ColaArregloEstatico(capacidad_legado)  # espejo para comparar
        self._azar = random.Random(semilla)
        self._siguiente_id = ID_INICIAL
        self.recibidas = 0
        self.procesadas = 0
        self.rechazadas = 0
        self.revertidas = 0

    # ------------------------------------------------------------ entrada
    def recibir(self, origen, destino, monto, canal):
        """Valida y encola una transferencia nueva. O(1) + O(log n) del índice."""
        origen, destino = _normalizar_cuenta(origen), _normalizar_cuenta(destino)
        if origen == destino:
            raise ValueError("La cuenta de origen y destino no pueden ser iguales")
        monto = round(float(monto), 2)
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero")
        t = Transferencia(self._siguiente_id, origen, destino, monto, canal)
        self._siguiente_id += 1
        self.cola_principal.encolar(t)
        self.indice.insertar(t.id, t)
        self.legado.encolar(t.id)     # el legado recibe exactamente el mismo flujo
        self.recibidas += 1
        return t

    def generar_pico(self, cantidad):
        """Simula 'cantidad' llegadas simultáneas (pico de operaciones)."""
        for _ in range(int(cantidad)):
            origen = "200" + "".join(self._azar.choice("0123456789") for _ in range(10))
            destino = "300" + "".join(self._azar.choice("0123456789") for _ in range(10))
            monto = round(self._azar.lognormvariate(5.3, 1.0), 2)
            self.recibir(origen, destino, max(monto, 1.0), self._azar.choice(CANALES))
        return cantidad

    # ------------------------------------------------------------ proceso
    def procesar_siguiente(self):
        """Atiende la transferencia del frente de la cola principal."""
        if self.cola_principal.esta_vacia():
            return None
        t = self.cola_principal.desencolar()
        self.legado.desencolar()
        self._atender(t)
        return t

    def procesar_lote(self, cantidad):
        atendidas = 0
        while atendidas < cantidad and self.procesar_siguiente() is not None:
            atendidas += 1
        return atendidas

    def procesar_reintentos(self):
        """Atiende una vez a cada transferencia que estaba en reintento."""
        pendientes = len(self.cola_reintentos)   # se fija antes: evita ciclos
        for _ in range(pendientes):
            self._atender(self.cola_reintentos.desencolar())
        return pendientes

    def _atender(self, t):
        t.intentos += 1
        respuesta = self.switch.validar(t)
        if respuesta is Respuesta.APROBADA:
            t.estado, t.motivo = Estado.PROCESADA, ""
            self.pila_reversiones.apilar(t)
            self.procesadas += 1
            self._registrar(t, "Procesada", f"intento {t.intentos}")
        elif respuesta is Respuesta.FALLA_TEMPORAL and t.intentos < MAX_INTENTOS:
            t.estado, t.motivo = Estado.EN_REINTENTO, "Sin respuesta del switch"
            self.cola_reintentos.encolar(t)
            self._registrar(t, "Reintento programado", f"intento {t.intentos} de {MAX_INTENTOS}")
        else:
            t.motivo = ("Fondos insuficientes" if respuesta is Respuesta.FONDOS_INSUFICIENTES
                        else f"Sin respuesta tras {MAX_INTENTOS} intentos")
            t.estado = Estado.RECHAZADA
            self.rechazadas += 1
            self._registrar(t, "Rechazada", t.motivo)
            self.notificaciones.encolar(
                f"Cliente notificado: transferencia #{t.id} por S/ {t.monto:,.2f} "
                f"no se completó ({t.motivo.lower()}).")

    # ------------------------------------------------------------ reversión
    def revertir_ultima(self):
        """Deshace la última transferencia aprobada (LIFO)."""
        if self.pila_reversiones.esta_vacia():
            return None
        t = self.pila_reversiones.desapilar()
        t.estado, t.motivo = Estado.REVERTIDA, "Reversión solicitada"
        self.revertidas += 1
        self._registrar(t, "Revertida", "devolución a cuenta de origen")
        return t

    # ------------------------------------------------------------ consulta
    def buscar(self, id_transferencia):
        t = self.indice.buscar(int(id_transferencia))
        return t, self.indice.comparaciones_ultima_busqueda

    def resumen(self):
        return {
            "recibidas": self.recibidas,
            "en_cola": len(self.cola_principal),
            "en_reintento": len(self.cola_reintentos),
            "procesadas": self.procesadas,
            "rechazadas": self.rechazadas,
            "revertidas": self.revertidas,
            "pila": len(self.pila_reversiones),
            "indice": len(self.indice),
            "altura_avl": self.indice.altura(),
            "historial": len(self.historial),
            "legado_en_cola": len(self.legado),
            "legado_descartadas": self.legado.descartadas,
        }

    def sin_perdidas(self):
        """Invariante: toda transferencia recibida tiene un destino visible."""
        return self.recibidas == (len(self.cola_principal) + len(self.cola_reintentos)
                                  + self.procesadas + self.rechazadas)

    def _registrar(self, t, tipo, detalle):
        self.historial.agregar_al_final(Evento(datetime.now(), t.id, tipo, t.monto, detalle))
