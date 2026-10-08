"""Pila LIFO implementada con nodos enlazados.

En el motor se usa como pila de reversiones: la última transferencia aprobada
es la primera que se puede revertir (deshacer), igual que un "Ctrl+Z".
"""
from .nodos import Nodo


class PilaVaciaError(Exception):
    """Se lanza al desapilar o consultar una pila sin elementos."""


class PilaEnlazada:
    def __init__(self):
        self._cima = None
        self._tamano = 0

    def apilar(self, dato):
        """Coloca un dato en la cima. O(1)."""
        self._cima = Nodo(dato, self._cima)  # el nuevo nodo apunta a la cima anterior
        self._tamano += 1

    def desapilar(self):
        """Retira y devuelve el dato de la cima. O(1)."""
        if self._cima is None:
            raise PilaVaciaError("La pila está vacía")
        nodo = self._cima
        self._cima = nodo.siguiente
        nodo.siguiente = None
        self._tamano -= 1
        return nodo.dato

    def cima(self):
        if self._cima is None:
            raise PilaVaciaError("La pila está vacía")
        return self._cima.dato

    def esta_vacia(self):
        return self._tamano == 0

    def primeros(self, k):
        """Hasta k datos desde la cima hacia abajo (para la vista gráfica)."""
        datos, actual = [], self._cima
        while actual is not None and len(datos) < k:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos

    def __len__(self):
        return self._tamano

    def __iter__(self):
        actual = self._cima
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
