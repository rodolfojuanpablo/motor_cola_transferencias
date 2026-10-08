"""Nodos: la unidad mínima que enlaza dinámicamente los datos en memoria.

Cada nodo se crea solo cuando llega un dato nuevo, por eso ninguna estructura
del proyecto necesita reservar un número fijo de posiciones (a diferencia del
arreglo estático de 5 000 casillas del módulo legado).
"""


class Nodo:
    """Nodo simple: guarda un dato y la referencia al siguiente nodo.
    Lo usan la ColaEnlazada y la PilaEnlazada."""
    __slots__ = ("dato", "siguiente")

    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente


class NodoDoble:
    """Nodo con dos enlaces (anterior y siguiente). Lo usa la ListaDobleEnlazada
    para poder recorrer el historial en ambos sentidos."""
    __slots__ = ("dato", "anterior", "siguiente")

    def __init__(self, dato, anterior=None, siguiente=None):
        self.dato = dato
        self.anterior = anterior
        self.siguiente = siguiente


class NodoAVL:
    """Nodo de árbol AVL: clave de búsqueda, valor asociado, hijos y altura."""
    __slots__ = ("clave", "valor", "izq", "der", "altura")

    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izq = None
        self.der = None
        self.altura = 1  # una hoja tiene altura 1
