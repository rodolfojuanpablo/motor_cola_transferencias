"""Cola FIFO implementada con nodos enlazados.

Reemplaza al arreglo estático del módulo legado: crece mientras haya memoria,
y tanto encolar como desencolar cuestan O(1) porque se mantienen dos
referencias (frente y final) y nunca se desplazan elementos.
"""
from .nodos import Nodo


class ColaVaciaError(Exception):
    """Se lanza al intentar desencolar o consultar una cola sin elementos."""


class ColaEnlazada:
    def __init__(self):
        self._frente = None   # primer nodo en ser atendido
        self._final = None    # último nodo en llegar
        self._tamano = 0

    def encolar(self, dato):
        """Agrega un dato al final de la cola. O(1)."""
        nuevo = Nodo(dato)
        if self._final is None:          # cola vacía: el nodo es frente y final
            self._frente = nuevo
        else:
            self._final.siguiente = nuevo  # el antiguo final apunta al nuevo nodo
        self._final = nuevo
        self._tamano += 1

    def desencolar(self):
        """Retira y devuelve el dato del frente. O(1)."""
        if self._frente is None:
            raise ColaVaciaError("La cola está vacía")
        nodo = self._frente
        self._frente = nodo.siguiente
        if self._frente is None:         # se retiró el único elemento
            self._final = None
        nodo.siguiente = None            # se desconecta para liberar memoria
        self._tamano -= 1
        return nodo.dato

    def ver_frente(self):
        if self._frente is None:
            raise ColaVaciaError("La cola está vacía")
        return self._frente.dato

    def ver_final(self):
        if self._final is None:
            raise ColaVaciaError("La cola está vacía")
        return self._final.dato

    def esta_vacia(self):
        return self._tamano == 0

    def primeros(self, k):
        """Devuelve hasta k datos desde el frente (para la vista gráfica). O(k)."""
        datos, actual = [], self._frente
        while actual is not None and len(datos) < k:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos

    def __len__(self):
        return self._tamano

    def __iter__(self):
        actual = self._frente
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
