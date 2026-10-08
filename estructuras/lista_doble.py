"""Lista doblemente enlazada.

Guarda el historial de eventos del motor. Los dos enlaces de cada nodo permiten
paginar el historial hacia adelante y hacia atrás sin recorrerlo desde el
inicio, e insertar al final en O(1).
"""
from .nodos import NodoDoble


class ListaDobleEnlazada:
    def __init__(self):
        self.cabeza = None   # evento más antiguo
        self.cola = None     # evento más reciente
        self._tamano = 0

    def agregar_al_final(self, dato):
        """Inserta un dato después del último nodo. O(1)."""
        nuevo = NodoDoble(dato, anterior=self.cola)
        if self.cola is None:
            self.cabeza = nuevo
        else:
            self.cola.siguiente = nuevo
        self.cola = nuevo
        self._tamano += 1
        return nuevo

    def agregar_al_inicio(self, dato):
        """Inserta un dato antes del primer nodo. O(1)."""
        nuevo = NodoDoble(dato, siguiente=self.cabeza)
        if self.cabeza is None:
            self.cola = nuevo
        else:
            self.cabeza.anterior = nuevo
        self.cabeza = nuevo
        self._tamano += 1
        return nuevo

    def eliminar_nodo(self, nodo):
        """Desenlaza un nodo conocido en O(1) reconectando a sus vecinos."""
        if nodo.anterior is None:
            self.cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self.cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        nodo.anterior = nodo.siguiente = None
        self._tamano -= 1
        return nodo.dato

    def desplazar(self, nodo, pasos, hacia_atras=True):
        """Avanza 'pasos' nodos desde 'nodo' (sin salirse de la lista).
        Lo usa la interfaz para pasar de página en el historial."""
        actual = nodo
        for _ in range(pasos):
            vecino = actual.anterior if hacia_atras else actual.siguiente
            if vecino is None:
                break
            actual = vecino
        return actual

    def recorrer(self, desde=None, hacia_atras=False, limite=None):
        """Genera datos desde un nodo en el sentido indicado."""
        if desde is None:
            desde = self.cola if hacia_atras else self.cabeza
        actual, n = desde, 0
        while actual is not None and (limite is None or n < limite):
            yield actual.dato
            actual = actual.anterior if hacia_atras else actual.siguiente
            n += 1

    def __len__(self):
        return self._tamano

    def __iter__(self):
        return self.recorrer()
