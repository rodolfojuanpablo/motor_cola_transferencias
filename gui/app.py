"""Interfaz gráfica (Tkinter) del prototipo de motor de cola de transferencias.

La interfaz no contiene lógica de negocio: solo llama al MotorTransferencias y
dibuja el estado de sus estructuras dinámicas.
"""
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import messagebox, ttk

from dominio.motor import MotorTransferencias
from dominio.transferencia import CANALES

NAVY = "#0B2545"
AZUL = "#1F4E79"
VERDE = "#00A651"
AMBAR = "#E8A33D"
ROJO = "#C0392B"
MORADO = "#6C3483"
FONDO = "#F4F6F9"
GRIS = "#5D6D7E"
BORDE = "#D5DBE3"
FILAS_POR_PAGINA = 11


def _familia_disponible(root):
    familias = set(tkfont.families(root))
    for f in ("Segoe UI", "Helvetica Neue", "DejaVu Sans", "Arial"):
        if f in familias:
            return f
    return "TkDefaultFont"


class AplicacionMotor(tk.Tk):
    def __init__(self, motor=None):
        super().__init__()
        self.motor = motor or MotorTransferencias()
        self.title("Motor de Cola de Transferencias — Prototipo con estructuras dinámicas")
        self.geometry("1320x800")
        self.minsize(1180, 740)
        self.configure(bg=FONDO)
        self.f = _familia_disponible(self)
        self._cursor_historial = None
        self._pagina = 1
        self._estilos()
        self._construir()
        self.refrescar()

    # ------------------------------------------------------------------ UI
    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", font=(self.f, 10), background=FONDO)
        s.configure("Panel.TFrame", background="white")
        s.configure("Panel.TLabelframe", background="white", bordercolor=BORDE)
        s.configure("Panel.TLabelframe.Label", background="white", foreground=AZUL,
                    font=(self.f, 10, "bold"))
        s.configure("Panel.TLabel", background="white", foreground="#2C3E50")
        s.configure("Accion.TButton", font=(self.f, 10, "bold"), foreground="white",
                    background=AZUL, padding=(8, 5), borderwidth=0)
        s.map("Accion.TButton", background=[("active", NAVY)])
        s.configure("Pico.TButton", font=(self.f, 10, "bold"), foreground="white",
                    background=VERDE, padding=(8, 5), borderwidth=0)
        s.map("Pico.TButton", background=[("active", "#00813F")])
        s.configure("Sec.TButton", padding=(8, 4))
        s.configure("Treeview", font=(self.f, 9), rowheight=21)
        s.configure("Treeview.Heading", font=(self.f, 9, "bold"), foreground="white",
                    background=AZUL)
        s.map("Treeview.Heading", background=[("active", NAVY)])
        s.configure("TNotebook.Tab", font=(self.f, 10, "bold"), padding=(12, 4))

    def _construir(self):
        # Encabezado
        cab = tk.Frame(self, bg=NAVY, height=58)
        cab.pack(fill="x")
        tk.Label(cab, text="Motor de Cola de Transferencias", bg=NAVY, fg="white",
                 font=(self.f, 16, "bold")).pack(side="left", padx=(18, 10), pady=10)
        tk.Label(cab, text="Prototipo · listas enlazadas, colas, pila y árbol AVL",
                 bg=NAVY, fg="#AFC4DA", font=(self.f, 10)).pack(side="left", pady=14)
        self.lbl_invariante = tk.Label(cab, bg=VERDE, fg="white", font=(self.f, 10, "bold"),
                                       padx=12, pady=4)
        self.lbl_invariante.pack(side="right", padx=18)

        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=10)
        self._panel_control(cuerpo)
        derecha = tk.Frame(cuerpo, bg=FONDO)
        derecha.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self._tarjetas(derecha)
        self.lienzo = tk.Canvas(derecha, height=250, bg="white", highlightthickness=1,
                                highlightbackground=BORDE)
        self.lienzo.pack(fill="x", pady=(8, 8))
        abajo = tk.Frame(derecha, bg=FONDO)
        abajo.pack(fill="both", expand=True)
        self._pestanas(abajo)
        self.comparativo = tk.Canvas(abajo, width=300, bg="white", highlightthickness=1,
                                     highlightbackground=BORDE)
        self.comparativo.pack(side="left", fill="y", padx=(8, 0))
        self.lienzo.bind("<Configure>", lambda e: self._dibujar_estructuras())

    def _panel_control(self, padre):
        p = ttk.Frame(padre, style="Panel.TFrame", padding=10)
        p.pack(side="left", fill="y")

        nf = ttk.LabelFrame(p, text="1 · Nueva transferencia", style="Panel.TLabelframe",
                            padding=8)
        nf.pack(fill="x")
        self.var_origen = tk.StringVar(value="200-3001234567")
        self.var_destino = tk.StringVar(value="300-7009876543")
        self.var_monto = tk.StringVar(value="1250.00")
        self.var_canal = tk.StringVar(value=CANALES[0])
        for fila, (texto, var) in enumerate((("Cuenta origen", self.var_origen),
                                             ("Cuenta destino", self.var_destino),
                                             ("Monto (S/)", self.var_monto))):
            ttk.Label(nf, text=texto, style="Panel.TLabel").grid(row=fila, column=0,
                                                                  sticky="w", pady=2)
            ttk.Entry(nf, textvariable=var, width=19).grid(row=fila, column=1, pady=2)
        ttk.Label(nf, text="Canal", style="Panel.TLabel").grid(row=3, column=0, sticky="w")
        ttk.Combobox(nf, textvariable=self.var_canal, values=CANALES, width=17,
                     state="readonly").grid(row=3, column=1, pady=2)
        ttk.Button(nf, text="Encolar transferencia", style="Accion.TButton",
                   command=self.encolar).grid(row=4, column=0, columnspan=2, sticky="ew",
                                              pady=(6, 0))

        pf = ttk.LabelFrame(p, text="2 · Pico de operaciones", style="Panel.TLabelframe",
                            padding=8)
        pf.pack(fill="x", pady=8)
        self.var_pico = tk.IntVar(value=6000)
        ttk.Label(pf, text="Llegadas simultáneas", style="Panel.TLabel").grid(row=0, column=0,
                                                                            sticky="w")
        ttk.Spinbox(pf, from_=100, to=200000, increment=500, textvariable=self.var_pico,
                    width=9).grid(row=0, column=1, padx=(6, 0))
        ttk.Button(pf, text="Simular pico", style="Pico.TButton",
                   command=self.simular_pico).grid(row=1, column=0, columnspan=2,
                                                   sticky="ew", pady=(6, 0))

        rf = ttk.LabelFrame(p, text="3 · Procesamiento", style="Panel.TLabelframe", padding=8)
        rf.pack(fill="x")
        self.var_lote = tk.IntVar(value=1000)
        ttk.Button(rf, text="Procesar siguiente (desencolar)", style="Sec.TButton",
                   command=self.procesar_uno).grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(rf, text="Tamaño de lote", style="Panel.TLabel").grid(row=1, column=0,
                                                                      sticky="w", pady=4)
        ttk.Spinbox(rf, from_=1, to=200000, increment=100, textvariable=self.var_lote,
                    width=9).grid(row=1, column=1, padx=(6, 0))
        ttk.Button(rf, text="Procesar lote", style="Accion.TButton",
                   command=self.procesar_lote).grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(rf, text="Atender cola de reintentos", style="Sec.TButton",
                   command=self.procesar_reintentos).grid(row=3, column=0, columnspan=2,
                                                          sticky="ew", pady=(6, 0))
        ttk.Button(rf, text="Revertir última aprobada (pila)", style="Sec.TButton",
                   command=self.revertir).grid(row=4, column=0, columnspan=2, sticky="ew",
                                               pady=(6, 0))

        bf = ttk.LabelFrame(p, text="4 · Consulta por ID (árbol AVL)",
                            style="Panel.TLabelframe", padding=8)
        bf.pack(fill="x", pady=8)
        self.var_buscar = tk.StringVar(value="100001")
        ttk.Entry(bf, textvariable=self.var_buscar, width=12).grid(row=0, column=0)
        ttk.Button(bf, text="Buscar", style="Accion.TButton",
                   command=self.buscar).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        self.lbl_busqueda = tk.Label(bf, text="Ingrese un ID y presione Buscar.", bg="white",
                                     fg=GRIS, justify="left", wraplength=240,
                                     font=(self.f, 9), anchor="w")
        self.lbl_busqueda.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def _tarjetas(self, padre):
        fila = tk.Frame(padre, bg=FONDO)
        fila.pack(fill="x")
        self.tarjetas = {}
        for clave, titulo, color in (("en_cola", "En cola principal", AZUL),
                                     ("en_reintento", "En reintento", AMBAR),
                                     ("procesadas", "Procesadas", VERDE),
                                     ("rechazadas", "Rechazadas notificadas", ROJO),
                                     ("pila", "Pila de reversión", MORADO),
                                     ("avl", "Índice AVL (n / altura)", NAVY)):
            c = tk.Frame(fila, bg="white", highlightthickness=1, highlightbackground=BORDE)
            c.pack(side="left", fill="x", expand=True, padx=(0, 6))
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            tk.Label(c, text=titulo, bg="white", fg=GRIS, font=(self.f, 9)).pack(
                anchor="w", padx=10, pady=(6, 0))
            v = tk.Label(c, text="0", bg="white", fg=color, font=(self.f, 18, "bold"))
            v.pack(anchor="w", padx=10, pady=(0, 6))
            self.tarjetas[clave] = v

    def _pestanas(self, padre):
        nb = ttk.Notebook(padre)
        nb.pack(side="left", fill="both", expand=True)
        h = tk.Frame(nb, bg="white")
        nb.add(h, text="Historial · lista doble")
        cols = ("hora", "id", "evento", "monto", "detalle")
        self.tabla = ttk.Treeview(h, columns=cols, show="headings", height=FILAS_POR_PAGINA)
        for col, txt, ancho in (("hora", "Hora", 66), ("id", "ID", 64),
                                ("evento", "Evento", 132), ("monto", "Monto (S/)", 82),
                                ("detalle", "Detalle", 190)):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=ancho, anchor="w" if col == "detalle" else "center")
        for tag, color in (("Procesada", "#1E8449"), ("Rechazada", ROJO),
                           ("Reintento programado", "#B9770E"), ("Revertida", MORADO)):
            self.tabla.tag_configure(tag, foreground=color)
        self.tabla.pack(fill="both", expand=True)
        nav = tk.Frame(h, bg="white")
        nav.pack(fill="x", pady=4)
        ttk.Button(nav, text="◀ Más recientes", style="Sec.TButton",
                   command=lambda: self._paginar(-1)).pack(side="left", padx=6)
        self.lbl_pagina = tk.Label(nav, text="", bg="white", fg=GRIS, font=(self.f, 9))
        self.lbl_pagina.pack(side="left", expand=True)
        ttk.Button(nav, text="Más antiguos ▶", style="Sec.TButton",
                   command=lambda: self._paginar(1)).pack(side="right", padx=6)

        b = tk.Frame(nb, bg="white")
        nb.add(b, text="Bitácora y notificaciones")
        self.bitacora = tk.Text(b, height=12, font=("DejaVu Sans Mono", 9), bg="#FBFCFD",
                                relief="flat", wrap="word")
        self.bitacora.pack(fill="both", expand=True, padx=4, pady=4)
        self.bitacora.tag_configure("alerta", foreground=ROJO)
        self.bitacora.tag_configure("ok", foreground="#1E8449")

    # ------------------------------------------------------------ acciones
    def encolar(self):
        try:
            t = self.motor.recibir(self.var_origen.get(), self.var_destino.get(),
                                   self.var_monto.get(), self.var_canal.get())
        except ValueError as e:
            messagebox.showerror("Datos no válidos", str(e))
            return
        self._log(f"Encolada #{t.id} · S/ {t.monto:,.2f} · {t.canal}", "ok")
        self.refrescar()

    def simular_pico(self):
        n = self._entero(self.var_pico, "Llegadas simultáneas")
        if n is None:
            return
        antes = self.motor.legado.descartadas
        self.motor.generar_pico(n)
        perdidas = self.motor.legado.descartadas - antes
        self._log(f"Pico de {n:,} llegadas: cola dinámica aceptó {n:,} · "
                  f"arreglo legado habría descartado {perdidas:,}.",
                  "alerta" if perdidas else "ok")
        self.refrescar()

    def procesar_uno(self):
        t = self.motor.procesar_siguiente()
        if t is None:
            messagebox.showinfo("Cola vacía", "No hay transferencias pendientes.")
            return
        self._log(f"Atendida #{t.id} → {t.estado.value}")
        self.refrescar()

    def procesar_lote(self):
        n = self._entero(self.var_lote, "Tamaño de lote")
        if n is None:
            return
        antes = (self.motor.procesadas, self.motor.rechazadas)
        atendidas = self.motor.procesar_lote(n)
        self._log(f"Lote: {atendidas:,} atendidas · {self.motor.procesadas - antes[0]:,} "
                  f"aprobadas · {len(self.motor.cola_reintentos):,} en reintento · "
                  f"{self.motor.rechazadas - antes[1]:,} rechazadas.")
        self.refrescar()

    def procesar_reintentos(self):
        n = self.motor.procesar_reintentos()
        self._log(f"Ronda de reintentos: {n:,} transferencias reprocesadas.")
        self.refrescar()

    def revertir(self):
        t = self.motor.revertir_ultima()
        if t is None:
            messagebox.showinfo("Pila vacía", "No hay transferencias aprobadas por revertir.")
            return
        self._log(f"Revertida #{t.id} (S/ {t.monto:,.2f}) — se desapiló de la cima.", "alerta")
        self.refrescar()

    def buscar(self):
        try:
            t, comps = self.motor.buscar(self.var_buscar.get())
        except ValueError:
            messagebox.showerror("ID no válido", "El ID debe ser un número entero.")
            return
        altura = self.motor.indice.altura()
        if t is None:
            texto, color = f"No existe. Búsqueda resuelta en {comps} comparación(es).", ROJO
        else:
            texto = (f"#{t.id} · {t.estado.value}\nS/ {t.monto:,.2f} · {t.canal} · "
                     f"intentos: {t.intentos}\nEncontrada en {comps} "
                     f"{'comparación' if comps == 1 else 'comparaciones'} "
                     f"(altura del árbol: {altura}; n = {len(self.motor.indice):,}).")
            color = AZUL
        self.lbl_busqueda.configure(text=texto, fg=color)

    # ------------------------------------------------------------ refresco
    def refrescar(self):
        r = self.motor.resumen()
        self.tarjetas["en_cola"].configure(text=f"{r['en_cola']:,}")
        self.tarjetas["en_reintento"].configure(text=f"{r['en_reintento']:,}")
        self.tarjetas["procesadas"].configure(text=f"{r['procesadas']:,}")
        self.tarjetas["rechazadas"].configure(text=f"{r['rechazadas']:,}")
        self.tarjetas["pila"].configure(text=f"{r['pila']:,}")
        self.tarjetas["avl"].configure(text=f"{r['indice']:,} / {r['altura_avl']}")
        ok = self.motor.sin_perdidas()
        self.lbl_invariante.configure(
            text=("✔ 0 transferencias perdidas" if ok else "✖ Inconsistencia detectada"),
            bg=VERDE if ok else ROJO)
        while not self.motor.notificaciones.esta_vacia():
            self._log(self.motor.notificaciones.desencolar(), "alerta")
        self._cursor_historial, self._pagina = self.motor.historial.cola, 1
        self._llenar_tabla()
        self._dibujar_estructuras()
        self._dibujar_comparativo()

    def _llenar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        total = len(self.motor.historial)
        if self._cursor_historial is not None:
            for ev in self.motor.historial.recorrer(self._cursor_historial, hacia_atras=True,
                                                    limite=FILAS_POR_PAGINA):
                self.tabla.insert("", "end", tags=(ev.tipo,),
                                  values=(ev.hora.strftime("%H:%M:%S"), ev.id_transferencia,
                                          ev.tipo, f"{ev.monto:,.2f}", ev.detalle))
        paginas = max(1, -(-total // FILAS_POR_PAGINA))
        self.lbl_pagina.configure(text=f"Página {self._pagina} de {paginas} · "
                                       f"{total:,} eventos")

    def _paginar(self, sentido):
        if self._cursor_historial is None:
            return
        hacia_atras = sentido > 0
        nuevo = self.motor.historial.desplazar(self._cursor_historial, FILAS_POR_PAGINA,
                                               hacia_atras=hacia_atras)
        paginas = max(1, -(-len(self.motor.historial) // FILAS_POR_PAGINA))
        siguiente = self._pagina + sentido
        if nuevo is self._cursor_historial or not 1 <= siguiente <= paginas:
            return
        self._cursor_historial, self._pagina = nuevo, siguiente
        self._llenar_tabla()

    # ------------------------------------------------------------ dibujo
    def _caja(self, c, x, y, w, h, l1, l2, color, relleno="white"):
        c.create_rectangle(x, y, x + w, y + h, outline=color, width=2, fill=relleno)
        c.create_line(x + w - 16, y, x + w - 16, y + h, fill=color)     # campo "siguiente"
        c.create_text(x + (w - 16) / 2, y + h / 2 - 8, text=l1, fill=color,
                      font=(self.f, 9, "bold"))
        c.create_text(x + (w - 16) / 2, y + h / 2 + 9, text=l2, fill=GRIS, font=(self.f, 8))

    def _flecha(self, c, x1, y, x2, color=GRIS):
        c.create_line(x1, y, x2, y, arrow="last", fill=color, width=2)

    def _fila_cola(self, c, x0, y, cola, titulo, color, max_visibles):
        total = len(cola)
        c.create_text(x0, y - 30, text=f"{titulo}  ({total:,} nodos)", anchor="w",
                      fill=color, font=(self.f, 10, "bold"))
        if total == 0:
            c.create_text(x0, y + 22, text="frente = final = None  (cola vacía)", anchor="w",
                          fill=GRIS, font=(self.f, 9, "italic"))
            return
        w, h, sep = 98, 44, 26
        visibles = cola.primeros(max_visibles if total <= max_visibles else max_visibles - 1)
        x = x0
        for i, t in enumerate(visibles):
            self._caja(c, x, y, w, h, f"#{t.id}", f"S/ {t.monto:,.0f}", color)
            if i == 0:
                c.create_text(x + 40, y - 10, text="FRENTE", fill=color, font=(self.f, 8, "bold"))
            self._flecha(c, x + w - 8, y + h / 2, x + w + sep)
            x += w + sep
        if total > max_visibles:
            ocultos = total - len(visibles) - 1
            c.create_text(x + 36, y + h / 2, text=f"⋯ {ocultos:,}", fill=GRIS,
                          font=(self.f, 10, "bold"))
            self._flecha(c, x + 72, y + h / 2, x + 72 + sep)
            x += 72 + sep
            ultimo = cola.ver_final()
            self._caja(c, x, y, w, h, f"#{ultimo.id}", f"S/ {ultimo.monto:,.0f}", color)
            c.create_text(x + 40, y - 10, text="FINAL", fill=color, font=(self.f, 8, "bold"))
            self._flecha(c, x + w - 8, y + h / 2, x + w + sep)
            x += w + sep
        elif total == len(visibles):
            c.create_text(x - sep - w + 40, y - 10, text="FINAL" if total > 1 else "",
                          fill=color, font=(self.f, 8, "bold"))
        c.create_text(x + 16, y + h / 2, text="None", fill=GRIS, font=(self.f, 9, "italic"))

    def _dibujar_estructuras(self):
        c = self.lienzo
        c.delete("all")
        ancho = max(c.winfo_width(), 900)
        x_pila = ancho - 200
        visibles = max(3, int((x_pila - 90) // 124) - 1)
        self._fila_cola(c, 18, 52, self.motor.cola_principal, "Cola principal (FIFO)",
                        AZUL, visibles)
        self._fila_cola(c, 18, 172, self.motor.cola_reintentos,
                        "Cola de reintentos (máx. 3 intentos)", "#B9770E", visibles)
        # Pila de reversión
        pila = self.motor.pila_reversiones
        c.create_line(x_pila - 16, 14, x_pila - 16, 236, fill=BORDE)
        c.create_text(x_pila, 22, text=f"Pila de reversión ({len(pila):,})", anchor="w",
                      fill=MORADO, font=(self.f, 10, "bold"))
        y = 56
        tope = pila.primeros(4)
        if not tope:
            c.create_text(x_pila, 70, text="cima = None", anchor="w", fill=GRIS,
                          font=(self.f, 9, "italic"))
        for i, t in enumerate(tope):
            relleno = "#F4ECF7" if i == 0 else "white"
            c.create_rectangle(x_pila, y, x_pila + 140, y + 36, outline=MORADO, width=2,
                               fill=relleno)
            c.create_text(x_pila + 70, y + 12, text=f"#{t.id}", fill=MORADO,
                          font=(self.f, 9, "bold"))
            c.create_text(x_pila + 70, y + 26, text=f"S/ {t.monto:,.2f}", fill=GRIS,
                          font=(self.f, 8))
            if i == 0:
                c.create_text(x_pila + 70, y - 9, text="CIMA ▼", fill=MORADO,
                              font=(self.f, 8, "bold"))
            y += 41
        if len(pila) > 4:
            c.create_text(x_pila + 70, y + 8, text=f"⋮ {len(pila) - 4:,} más", fill=GRIS,
                          font=(self.f, 9, "bold"))

    def _dibujar_comparativo(self):
        c = self.comparativo
        c.delete("all")
        r = self.motor.resumen()
        recibidas, desc = r["recibidas"], r["legado_descartadas"]
        c.create_text(14, 18, text="Mismo flujo de llegadas", anchor="w", fill=AZUL,
                      font=(self.f, 11, "bold"))
        c.create_text(14, 38, text="Arreglo estático (5 000) vs. cola enlazada", anchor="w",
                      fill=GRIS, font=(self.f, 9))
        base = max(recibidas, 1)
        largo = 268
        filas = (("Módulo legado", recibidas - desc, desc, "#7F8C8D"),
                 ("Cola dinámica", recibidas, 0, VERDE))
        y = 72
        for nombre, aceptadas, perdidas, color in filas:
            c.create_text(14, y, text=nombre, anchor="w", fill="#2C3E50",
                          font=(self.f, 10, "bold"))
            wa = largo * aceptadas / base
            c.create_rectangle(14, y + 12, 14 + wa, y + 36, fill=color, outline="")
            if perdidas:
                c.create_rectangle(14 + wa, y + 12, 14 + largo, y + 36, fill=ROJO, outline="")
            c.create_text(14, y + 50, anchor="w", fill=GRIS, font=(self.f, 9),
                          text=f"Aceptadas {aceptadas:,}   ·   Descartadas {perdidas:,}")
            y += 82
        c.create_rectangle(14, y, 26, y + 12, fill=ROJO, outline="")
        c.create_text(32, y + 6, anchor="w", fill=GRIS, font=(self.f, 9),
                      text="pérdida silenciosa (sin reintento ni aviso)")
        ocup = r["legado_en_cola"]
        c.create_text(14, y + 34, anchor="w", fill="#2C3E50", font=(self.f, 9),
                      text=f"Ocupación del arreglo legado: {ocup:,} / 5 000")
        c.create_rectangle(14, y + 46, 14 + largo, y + 56, outline=BORDE)
        c.create_rectangle(14, y + 46, 14 + largo * ocup / 5000, y + 56,
                           fill=ROJO if ocup >= 5000 else "#7F8C8D", outline="")

    # ------------------------------------------------------------ utilidades
    def _entero(self, var, nombre):
        try:
            n = int(var.get())
            if n <= 0:
                raise ValueError
            return n
        except (ValueError, tk.TclError):
            messagebox.showerror("Dato no válido", f"{nombre} debe ser un entero positivo.")
            return None

    def _log(self, texto, tag=None):
        self.bitacora.insert("1.0", f"[{datetime.now():%H:%M:%S}] {texto}\n", tag or ())
