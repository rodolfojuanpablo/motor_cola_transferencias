"""Árbol AVL (árbol binario de búsqueda autobalanceado).

Indexa cada transferencia por su ID para consultar su estado en O(log n).
Los IDs llegan en orden creciente: en un árbol binario simple eso produciría
una "rama" de altura n (equivalente a una lista). Las rotaciones AVL mantienen
la altura cerca de log2(n) en todo momento.
"""
from .nodos import NodoAVL


def _altura(nodo):
    return nodo.altura if nodo else 0


def _actualizar(nodo):
    nodo.altura = 1 + max(_altura(nodo.izq), _altura(nodo.der))


def _balance(nodo):
    return _altura(nodo.izq) - _altura(nodo.der)


def _rotar_derecha(y):
    x = y.izq
    y.izq = x.der
    x.der = y
    _actualizar(y)
    _actualizar(x)
    return x


def _rotar_izquierda(x):
    y = x.der
    x.der = y.izq
    y.izq = x
    _actualizar(x)
    _actualizar(y)
    return y


class ArbolAVL:
    def __init__(self):
        self.raiz = None
        self._tamano = 0
        self.comparaciones_ultima_busqueda = 0

    def insertar(self, clave, valor):
        """Inserta (o actualiza) una clave. O(log n)."""
        self.raiz = self._insertar(self.raiz, clave, valor)

    def _insertar(self, nodo, clave, valor):
        if nodo is None:
            self._tamano += 1
            return NodoAVL(clave, valor)
        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave, valor)
        elif clave > nodo.clave:
            nodo.der = self._insertar(nodo.der, clave, valor)
        else:                       # clave repetida: se actualiza el valor
            nodo.valor = valor
            return nodo

        _actualizar(nodo)
        b = _balance(nodo)
        # Los cuatro casos de desbalance (|b| > 1) y su rotación correctora
        if b > 1 and clave < nodo.izq.clave:        # izquierda-izquierda
            return _rotar_derecha(nodo)
        if b < -1 and clave > nodo.der.clave:       # derecha-derecha
            return _rotar_izquierda(nodo)
        if b > 1 and clave > nodo.izq.clave:        # izquierda-derecha
            nodo.izq = _rotar_izquierda(nodo.izq)
            return _rotar_derecha(nodo)
        if b < -1 and clave < nodo.der.clave:       # derecha-izquierda
            nodo.der = _rotar_derecha(nodo.der)
            return _rotar_izquierda(nodo)
        return nodo

    def buscar(self, clave):
        """Devuelve el valor asociado o None. Cuenta las comparaciones hechas."""
        actual, comparaciones = self.raiz, 0
        while actual is not None:
            comparaciones += 1
            if clave == actual.clave:
                self.comparaciones_ultima_busqueda = comparaciones
                return actual.valor
            actual = actual.izq if clave < actual.clave else actual.der
        self.comparaciones_ultima_busqueda = comparaciones
        return None

    def __contains__(self, clave):
        return self.buscar(clave) is not None

    def altura(self):
        return _altura(self.raiz)

    def en_orden(self):
        """Recorrido in-orden iterativo: devuelve las claves ordenadas."""
        pila, actual = [], self.raiz
        while pila or actual:
            while actual:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            yield actual.clave, actual.valor
            actual = actual.der

    def __len__(self):
        return self._tamano
