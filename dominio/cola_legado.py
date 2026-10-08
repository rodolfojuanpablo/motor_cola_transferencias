"""Réplica del módulo legado: cola sobre un arreglo estático circular.

Se conserva solo para comparar. Reproduce la falla del caso: cuando las 5 000
posiciones están ocupadas, 'encolar' descarta la solicitud en silencio
(devuelve False y únicamente aumenta un contador interno).
"""


class ColaArregloEstatico:
    def __init__(self, capacidad=5000):
        self._datos = [None] * capacidad   # memoria reservada de antemano
        self._capacidad = capacidad
        self._inicio = 0
        self._tamano = 0
        self.descartadas = 0

    def encolar(self, dato):
        if self._tamano == self._capacidad:
            self.descartadas += 1          # pérdida silenciosa, sin reintento
            return False
        fin = (self._inicio + self._tamano) % self._capacidad
        self._datos[fin] = dato
        self._tamano += 1
        return True

    def desencolar(self):
        if self._tamano == 0:
            return None
        dato = self._datos[self._inicio]
        self._datos[self._inicio] = None
        self._inicio = (self._inicio + 1) % self._capacidad
        self._tamano -= 1
        return dato

    @property
    def capacidad(self):
        return self._capacidad

    def __len__(self):
        return self._tamano
