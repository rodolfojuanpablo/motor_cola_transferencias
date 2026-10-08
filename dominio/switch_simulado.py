"""Simula la respuesta del switch de pagos que autoriza cada transferencia.

En el prototipo no hay conexión real con el core bancario; las respuestas se
generan con probabilidades configurables y una semilla para que las pruebas
sean reproducibles.
"""
import random
from enum import Enum


class Respuesta(Enum):
    APROBADA = "aprobada"
    FALLA_TEMPORAL = "falla temporal"          # timeout del switch: se reintenta
    FONDOS_INSUFICIENTES = "fondos insuficientes"  # rechazo definitivo


class SwitchSimulado:
    def __init__(self, prob_falla_temporal=0.08, prob_fondos=0.02, semilla=None):
        self.prob_falla_temporal = prob_falla_temporal
        self.prob_fondos = prob_fondos
        self._azar = random.Random(semilla)

    def validar(self, transferencia):
        r = self._azar.random()
        if r < self.prob_fondos:
            return Respuesta.FONDOS_INSUFICIENTES
        if r < self.prob_fondos + self.prob_falla_temporal:
            return Respuesta.FALLA_TEMPORAL
        return Respuesta.APROBADA
