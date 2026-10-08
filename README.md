# Motor de Cola de Transferencias — estructuras dinámicas

Prototipo del curso **Estructuras de Datos (CIIN1190V)** para el caso *«El motor detrás de la cola»*:
reemplaza la cola estática de 5 000 posiciones del módulo de transferencias de Interbank por
estructuras de datos dinámicas implementadas desde cero, con interfaz gráfica en Tkinter.

## Cómo ejecutarlo

Requiere **Python 3.10 o superior**. No hay dependencias externas: todo usa la biblioteca estándar.

```bash
python main.py              # abre la interfaz gráfica
python -m unittest -v       # ejecuta las 14 pruebas unitarias
python benchmark.py         # mide tiempos frente a las alternativas (tarda ~10 s)
```

> En Linux, si aparece `ModuleNotFoundError: No module named 'tkinter'`, instalar `python3-tk`
> (`sudo apt install python3-tk`). En Windows y macOS Tkinter ya viene con Python.

Todos los comandos se ejecutan **desde la carpeta raíz del proyecto** (donde está `main.py`), porque los
módulos se importan como paquetes (`from estructuras import ...`).

## Estructura del proyecto

```
motor_cola_transferencias/
├── main.py                    Punto de entrada: crea y lanza la ventana
├── benchmark.py               Medición empírica de tiempos (sección V del informe)
├── estructuras/               Estructuras de datos dinámicas (no conocen el dominio bancario)
│   ├── nodos.py               Nodo (simple), NodoDoble y NodoAVL
│   ├── cola_enlazada.py       ColaEnlazada: FIFO, encolar/desencolar O(1)
│   ├── pila_enlazada.py       PilaEnlazada: LIFO, apilar/desapilar O(1)
│   ├── lista_doble.py         ListaDobleEnlazada: inserción O(1), recorrido en ambos sentidos
│   └── arbol_avl.py           ArbolAVL: insertar/buscar O(log n) con rotaciones de balance
├── dominio/                   Lógica de negocio (no conoce la interfaz)
│   ├── transferencia.py       Dataclasses Transferencia y Evento; enum Estado; lista CANALES
│   ├── switch_simulado.py     SwitchSimulado: responde aprobada / falla temporal / sin fondos
│   ├── cola_legado.py         ColaArregloEstatico: réplica del arreglo de 5 000 (solo para comparar)
│   └── motor.py               MotorTransferencias: orquesta todas las estructuras
├── gui/
│   └── app.py                 AplicacionMotor (tk.Tk): formulario, indicadores, dibujo de nodos
└── tests/
    └── test_estructuras.py    14 pruebas con unittest (estructuras, motor y legado)
```

## Qué estructura se usa y para qué

| Estructura | Dónde | Para qué | Costo |
|---|---|---|---|
| `ColaEnlazada` | `motor.cola_principal` | Atender transferencias en orden de llegada, sin límite fijo | O(1) |
| `ColaEnlazada` | `motor.cola_reintentos` | Reprocesar fallas temporales (máx. 3 intentos) sin bloquear la cola principal | O(1) |
| `ColaEnlazada` | `motor.notificaciones` | Mensajes de rechazo pendientes de mostrar al cliente | O(1) |
| `PilaEnlazada` | `motor.pila_reversiones` | Revertir la última transferencia aprobada (LIFO) | O(1) |
| `ListaDobleEnlazada` | `motor.historial` | Registro de eventos; la GUI lo pagina hacia adelante y atrás | O(1) / O(k) |
| `ArbolAVL` | `motor.indice` | Consultar el estado de una transferencia por ID | O(log n) |
| `ColaArregloEstatico` | `motor.legado` | Espejo del módulo antiguo: recibe el mismo flujo y cuenta lo que habría descartado | — |

## Flujo del motor (`dominio/motor.py`)

1. `recibir(origen, destino, monto, canal)` valida (cuentas de 13 dígitos y distintas, monto > 0),
   crea la `Transferencia`, la encola en `cola_principal`, la indexa en el AVL y la replica en el legado.
2. `procesar_siguiente()` desencola el frente y llama a `_atender(t)`, que consulta al switch:
   - **aprobada** → `pila_reversiones.apilar(t)`
   - **falla temporal** y `t.intentos < 3` → `cola_reintentos.encolar(t)`
   - **sin fondos** o 3 fallas → estado RECHAZADA + mensaje en `notificaciones`
   En todos los casos se agrega un `Evento` al final de `historial`.
3. `procesar_reintentos()` atiende una vez a cada transferencia que estaba en reintento
   (fija el tamaño antes de iterar para no atender dos veces a una reencolada).
4. `revertir_ultima()` desapila la cima y la marca como REVERTIDA.
5. `buscar(id)` consulta el AVL y devuelve también el número de comparaciones.
6. `sin_perdidas()` verifica el invariante: `recibidas = en cola + en reintento + procesadas + rechazadas`.

`MotorTransferencias(semilla=N)` hace reproducibles los datos aleatorios (picos y respuestas del switch).
Las capturas del informe usan `semilla=2026`.

## Interfaz (`gui/app.py`)

- **Panel izquierdo:** nueva transferencia, simulación de pico, procesamiento (uno, lote, reintentos),
  reversión y consulta por ID.
- **Tarjetas superiores:** tamaño de cada estructura y `n / altura` del AVL.
- **Lienzo central:** dibuja los primeros nodos de la cola principal y de reintentos (FRENTE → … → FINAL → None)
  y la cima de la pila.
- **Pestañas:** historial paginado (usa `ListaDobleEnlazada.desplazar`) y bitácora con las notificaciones.
- **Panel comparativo:** aceptadas vs. descartadas del legado frente a la cola dinámica con el mismo flujo.

La interfaz no contiene lógica de negocio: solo llama métodos del motor y vuelve a dibujar con `refrescar()`.

## Pruebas

`tests/test_estructuras.py` cubre: orden FIFO/LIFO, estructuras vacías, 100 000 elementos sin límite,
recorrido y eliminación en la lista doble, balance del AVL con 10 000 claves crecientes, pico de 6 000
sin pérdidas (legado pierde 1 000), conservación tras procesar, reversión LIFO, validaciones de entrada
y descarte silencioso del legado.

## Ideas para seguir

- Persistir la cola (archivo, SQLite o un gestor de mensajes) para no perder pendientes si el proceso se cae.
- Cola de prioridad (montículo) para transferencias urgentes.
- Eliminación en el AVL para depurar transferencias antiguas del índice.
