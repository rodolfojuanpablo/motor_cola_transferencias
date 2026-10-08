"""Pruebas unitarias de las estructuras dinámicas y del motor.
Ejecutar desde la raíz del proyecto:  python -m unittest -v
"""
import math
import unittest

from estructuras import (ArbolAVL, ColaEnlazada, ColaVaciaError, ListaDobleEnlazada,
                         PilaEnlazada, PilaVaciaError)
from dominio.cola_legado import ColaArregloEstatico
from dominio.motor import MotorTransferencias
from dominio.transferencia import Estado


class PruebaColaEnlazada(unittest.TestCase):
    def test_orden_fifo(self):
        c = ColaEnlazada()
        for i in range(5):
            c.encolar(i)
        self.assertEqual([c.desencolar() for _ in range(5)], [0, 1, 2, 3, 4])

    def test_sin_limite_fijo(self):
        c = ColaEnlazada()
        for i in range(100_000):          # 20 veces la capacidad del legado
            c.encolar(i)
        self.assertEqual(len(c), 100_000)
        self.assertEqual(c.ver_final(), 99_999)

    def test_cola_vacia(self):
        c = ColaEnlazada()
        c.encolar("a"); c.desencolar()
        self.assertTrue(c.esta_vacia())
        with self.assertRaises(ColaVaciaError):
            c.desencolar()


class PruebaPilaEnlazada(unittest.TestCase):
    def test_orden_lifo(self):
        p = PilaEnlazada()
        for i in range(4):
            p.apilar(i)
        self.assertEqual(p.cima(), 3)
        self.assertEqual([p.desapilar() for _ in range(4)], [3, 2, 1, 0])

    def test_pila_vacia(self):
        with self.assertRaises(PilaVaciaError):
            PilaEnlazada().desapilar()


class PruebaListaDoble(unittest.TestCase):
    def test_recorrido_en_ambos_sentidos(self):
        l = ListaDobleEnlazada()
        for i in range(1, 6):
            l.agregar_al_final(i)
        l.agregar_al_inicio(0)
        self.assertEqual(list(l), [0, 1, 2, 3, 4, 5])
        self.assertEqual(list(l.recorrer(hacia_atras=True)), [5, 4, 3, 2, 1, 0])

    def test_eliminar_y_desplazar(self):
        l = ListaDobleEnlazada()
        nodos = [l.agregar_al_final(i) for i in range(6)]
        l.eliminar_nodo(nodos[2])
        self.assertEqual(list(l), [0, 1, 3, 4, 5])
        self.assertEqual(l.desplazar(l.cola, 2).dato, 3)
        self.assertEqual(l.desplazar(l.cola, 99).dato, 0)   # no se sale de la lista


class PruebaArbolAVL(unittest.TestCase):
    def test_balance_con_claves_crecientes(self):
        a = ArbolAVL()
        n = 10_000
        for k in range(n):                # peor caso para un árbol binario simple
            a.insertar(k, f"t{k}")
        self.assertLessEqual(a.altura(), 1.45 * math.log2(n + 2))
        self.assertEqual([k for k, _ in a.en_orden()], list(range(n)))

    def test_busqueda(self):
        a = ArbolAVL()
        for k in (50, 20, 80, 10, 30, 70, 90):
            a.insertar(k, k * 2)
        self.assertEqual(a.buscar(70), 140)
        self.assertIsNone(a.buscar(65))
        self.assertLessEqual(a.comparaciones_ultima_busqueda, a.altura())


class PruebaMotor(unittest.TestCase):
    def test_pico_sin_perdidas_vs_legado(self):
        m = MotorTransferencias(semilla=7)
        m.generar_pico(6000)
        r = m.resumen()
        self.assertEqual(r["en_cola"], 6000)              # la cola dinámica acepta todo
        self.assertEqual(r["legado_descartadas"], 1000)   # el arreglo pierde 1 000
        self.assertTrue(m.sin_perdidas())

    def test_conservacion_tras_procesar(self):
        m = MotorTransferencias(semilla=11)
        m.generar_pico(3000)
        m.procesar_lote(3000)
        for _ in range(3):
            m.procesar_reintentos()
        self.assertTrue(m.sin_perdidas())
        self.assertEqual(len(m.cola_reintentos), 0)
        self.assertEqual(m.rechazadas, len(m.notificaciones))  # todo rechazo se notifica

    def test_reversion_lifo(self):
        m = MotorTransferencias(semilla=3)
        m.switch.prob_falla_temporal = m.switch.prob_fondos = 0.0
        ids = [m.recibir("2001234567890", "3009876543210", 100 + i, "Plin").id for i in range(3)]
        m.procesar_lote(3)
        t = m.revertir_ultima()
        self.assertEqual(t.id, ids[-1])
        self.assertEqual(t.estado, Estado.REVERTIDA)

    def test_validaciones_de_entrada(self):
        m = MotorTransferencias()
        with self.assertRaises(ValueError):
            m.recibir("123", "3009876543210", 50, "Plin")
        with self.assertRaises(ValueError):
            m.recibir("2001234567890", "2001234567890", 50, "Plin")
        with self.assertRaises(ValueError):
            m.recibir("2001234567890", "3009876543210", 0, "Plin")


class PruebaLegado(unittest.TestCase):
    def test_descarte_silencioso(self):
        c = ColaArregloEstatico(5000)
        aceptadas = sum(c.encolar(i) for i in range(5200))
        self.assertEqual((aceptadas, c.descartadas), (5000, 200))


if __name__ == "__main__":
    unittest.main(verbosity=2)
