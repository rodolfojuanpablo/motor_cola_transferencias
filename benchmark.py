"""Prueba empírica de eficiencia: python benchmark.py

Compara las estructuras elegidas contra las alternativas ingenuas:
  1) Cola: ColaEnlazada (O(1)) vs. lista de Python con pop(0) (O(n) por operación).
  2) Búsqueda por ID: árbol AVL (O(log n)) vs. búsqueda lineal en lista (O(n)).
"""
import random
import time

from estructuras import ArbolAVL, ColaEnlazada


def medir(fn, repeticiones=3):
    mejor = float("inf")
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        fn()
        mejor = min(mejor, time.perf_counter() - t0)
    return mejor * 1000  # ms


def cola_enlazada(n):
    c = ColaEnlazada()
    for i in range(n):
        c.encolar(i)
    while not c.esta_vacia():
        c.desencolar()


def lista_pop0(n):
    l = []
    for i in range(n):
        l.append(i)
    while l:
        l.pop(0)


def comparar_busquedas(n, consultas=2000, semilla=1):
    azar = random.Random(semilla)
    ids = list(range(100001, 100001 + n))
    arbol = ArbolAVL()
    for k in ids:
        arbol.insertar(k, None)
    objetivos = [azar.choice(ids) for _ in range(consultas)]
    t_avl = medir(lambda: [arbol.buscar(k) for k in objetivos])
    t_lin = medir(lambda: [ids.index(k) for k in objetivos], repeticiones=1)
    return t_avl, t_lin, arbol.altura()


def main():
    tamanos = [10_000, 20_000, 40_000, 80_000]
    print("n         | Cola enlazada (ms) | list.pop(0) (ms) | AVL 2000 búsq. (ms) "
          "| Lineal 2000 búsq. (ms) | Altura AVL")
    print("-" * 104)
    filas = []
    for n in tamanos:
        tc = medir(lambda: cola_enlazada(n))
        tl = medir(lambda: lista_pop0(n), repeticiones=1)
        ta, tb, h = comparar_busquedas(n)
        filas.append((n, tc, tl, ta, tb, h))
        print(f"{n:>9,} | {tc:>18.1f} | {tl:>16.1f} | {ta:>19.1f} | {tb:>22.1f} | {h:>10}")
    return filas


if __name__ == "__main__":
    main()
