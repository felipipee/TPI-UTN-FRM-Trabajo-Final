"""
main.py — Interfaz gráfica del TPI GeoData
Programación 1 — UTN

Punto de entrada de la aplicación. Contiene exclusivamente la capa de
presentación (ventanas, widgets, eventos). Toda la lógica de datos se
encuentra en funciones.py.

Dependencias externas:
    pip install customtkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from funciones import (
    cargar_csv,
    guardar_csv,
    obtener_ruta_csv_default,
    buscar_paises,
    filtrar_paises,
    ordenar_paises,
    ordenar_items_por_cantidad,
    calcular_estadisticas,
    validar_pais,
    nombre_duplicado,
    formatear_numero,
    CONTINENTES,
)


# ─────────────────────────────────────────────
#  PALETA Y CONFIGURACIÓN VISUAL
# ─────────────────────────────────────────────

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL_OSCURO  = "#0C447C"
AZUL_MED     = "#378ADD"
AZUL_CLARO   = "#B5D4F4"
BG_MAIN      = "#FFFFFF"
BG_SEC       = "#F5F5F3"
BG_SIDEBAR   = "#0C447C"
BORDE        = "#D3D1C7"
TEXTO        = "#1A1A1A"
TEXTO_MUTED  = "#6B6A65"


# ─────────────────────────────────────────────
#  VENTANA: AGREGAR / EDITAR PAÍS
# ─────────────────────────────────────────────

class VentanaPais(ctk.CTkToplevel):
    """
    Ventana modal para agregar un nuevo país o editar uno existente.

    Parámetros:
        parent: Ventana padre (App).
        pais (dict | None): Si se pasa, la ventana se abre en modo edición
            con los datos precargados. Si es None, modo agregar.
        callback (callable | None): Función a llamar al guardar.
            Recibe (nuevo_pais, pais_original).
    """

    def __init__(self, parent, pais=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.pais_original = pais
        titulo = "Editar país" if pais else "Agregar país"
        self.title(titulo)
        self.geometry("400x380")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)

        # Encabezado
        header = ctk.CTkFrame(self, fg_color=AZUL_OSCURO, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=titulo, font=("Helvetica", 14, "bold"),
                     text_color="white").pack(padx=20, pady=14, anchor="w")

        # Formulario
        form = ctk.CTkFrame(self, fg_color=BG_MAIN)
        form.pack(fill="both", expand=True, padx=24, pady=16)

        campos = [
            ("Nombre del país", "nombre",    "text"),
            ("Población (hab.)", "poblacion", "int"),
            ("Superficie (km²)", "superficie", "int"),
        ]
        self.entries = {}

        for label_txt, key, _tipo in campos:
            ctk.CTkLabel(form, text=label_txt, font=("Helvetica", 12),
                         text_color=TEXTO_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Helvetica", 13),
                                 fg_color=BG_SEC, border_color=BORDE, text_color=TEXTO,
                                 placeholder_text=f"Ingresá {label_txt.lower()}")
            entry.pack(fill="x")
            if pais:
                entry.insert(0, str(pais[key]))
            self.entries[key] = entry

        # Continente
        ctk.CTkLabel(form, text="Continente", font=("Helvetica", 12),
                     text_color=TEXTO_MUTED, anchor="w").pack(fill="x", pady=(8, 2))
        self.combo_cont = ctk.CTkComboBox(
            form, values=CONTINENTES, height=36,
            font=("Helvetica", 13), fg_color=BG_SEC,
            border_color=BORDE, text_color=TEXTO,
            button_color=AZUL_MED, dropdown_fg_color=BG_MAIN
        )
        self.combo_cont.pack(fill="x")
        if pais:
            self.combo_cont.set(pais["continente"])
        else:
            self.combo_cont.set("América")

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text="Cancelar", fg_color="transparent",
            border_width=1, border_color=BORDE, text_color=TEXTO,
            hover_color=BG_SEC, height=36, command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btn_frame, text="Guardar", fg_color=AZUL_OSCURO,
            hover_color=AZUL_MED, text_color="white",
            height=36, command=self._guardar
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _guardar(self):
        """Valida los datos del formulario y llama al callback si son correctos."""
        nombre  = self.entries["nombre"].get()
        pob_str = self.entries["poblacion"].get()
        sup_str = self.entries["superficie"].get()
        continente = self.combo_cont.get()

        es_valido, mensaje, poblacion, superficie = validar_pais(
            nombre, pob_str, sup_str, continente
        )
        if not es_valido:
            messagebox.showerror("Error", mensaje, parent=self)
            return

        pais = {
            "nombre": nombre.strip(),
            "poblacion": poblacion,
            "superficie": superficie,
            "continente": continente.strip(),
        }
        if self.callback:
            self.callback(pais, self.pais_original)
        self.destroy()


# ─────────────────────────────────────────────
#  VENTANA: FILTROS AVANZADOS
# ─────────────────────────────────────────────

class VentanaFiltros(ctk.CTkToplevel):
    """
    Ventana modal para ingresar rangos numéricos de población y superficie.

    Parámetros:
        parent: Ventana padre.
        filtros_actuales (dict): Filtros vigentes para precargar los campos.
        callback (callable): Función a llamar al aplicar o limpiar filtros.
            Recibe un dict con claves pob_min, pob_max, sup_min, sup_max.
    """

    def __init__(self, parent, filtros_actuales, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Filtros avanzados")
        self.geometry("360x320")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)

        header = ctk.CTkFrame(self, fg_color=AZUL_OSCURO, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Filtros avanzados", font=("Helvetica", 14, "bold"),
                     text_color="white").pack(padx=20, pady=14, anchor="w")

        form = ctk.CTkFrame(self, fg_color=BG_MAIN)
        form.pack(fill="both", expand=True, padx=24, pady=12)

        # Rango de población
        ctk.CTkLabel(form, text="Rango de población (hab.)", font=("Helvetica", 12, "bold"),
                     text_color=TEXTO).pack(anchor="w", pady=(0, 4))
        row_pob = ctk.CTkFrame(form, fg_color="transparent")
        row_pob.pack(fill="x")
        self.pob_min = ctk.CTkEntry(row_pob, placeholder_text="Mín.", width=120, height=34,
                                    fg_color=BG_SEC, border_color=BORDE, text_color=TEXTO)
        self.pob_min.pack(side="left")
        ctk.CTkLabel(row_pob, text="–", text_color=TEXTO_MUTED).pack(side="left", padx=8)
        self.pob_max = ctk.CTkEntry(row_pob, placeholder_text="Máx.", width=120, height=34,
                                    fg_color=BG_SEC, border_color=BORDE, text_color=TEXTO)
        self.pob_max.pack(side="left")

        # Rango de superficie
        ctk.CTkLabel(form, text="Rango de superficie (km²)", font=("Helvetica", 12, "bold"),
                     text_color=TEXTO).pack(anchor="w", pady=(14, 4))
        row_sup = ctk.CTkFrame(form, fg_color="transparent")
        row_sup.pack(fill="x")
        self.sup_min = ctk.CTkEntry(row_sup, placeholder_text="Mín.", width=120, height=34,
                                    fg_color=BG_SEC, border_color=BORDE, text_color=TEXTO)
        self.sup_min.pack(side="left")
        ctk.CTkLabel(row_sup, text="–", text_color=TEXTO_MUTED).pack(side="left", padx=8)
        self.sup_max = ctk.CTkEntry(row_sup, placeholder_text="Máx.", width=120, height=34,
                                    fg_color=BG_SEC, border_color=BORDE, text_color=TEXTO)
        self.sup_max.pack(side="left")

        # Precargar valores actuales
        f = filtros_actuales
        if f.get("pob_min") is not None:
            self.pob_min.insert(0, str(f["pob_min"]))
        if f.get("pob_max") is not None:
            self.pob_max.insert(0, str(f["pob_max"]))
        if f.get("sup_min") is not None:
            self.sup_min.insert(0, str(f["sup_min"]))
        if f.get("sup_max") is not None:
            self.sup_max.insert(0, str(f["sup_max"]))

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkButton(
            btn_frame, text="Limpiar filtros", fg_color="transparent",
            border_width=1, border_color=BORDE, text_color=TEXTO,
            hover_color=BG_SEC, height=36, command=self._limpiar
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            btn_frame, text="Aplicar", fg_color=AZUL_OSCURO,
            hover_color=AZUL_MED, text_color="white",
            height=36, command=self._aplicar
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _parse_int(self, entry):
        """Convierte el texto de un Entry a int, o None si está vacío o es inválido."""
        val = entry.get().strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def _aplicar(self):
        filtros = {
            "pob_min": self._parse_int(self.pob_min),
            "pob_max": self._parse_int(self.pob_max),
            "sup_min": self._parse_int(self.sup_min),
            "sup_max": self._parse_int(self.sup_max),
        }
        self.callback(filtros)
        self.destroy()

    def _limpiar(self):
        self.callback({"pob_min": None, "pob_max": None, "sup_min": None, "sup_max": None})
        self.destroy()


# ─────────────────────────────────────────────
#  VENTANA: ESTADÍSTICAS
# ─────────────────────────────────────────────

class VentanaEstadisticas(ctk.CTkToplevel):
    """
    Ventana modal con estadísticas descriptivas del dataset actual.

    Parámetros:
        parent: Ventana padre.
        paises (list): Lista de países sobre la que calcular estadísticas.
    """

    def __init__(self, parent, paises):
        super().__init__(parent)
        self.title("Estadísticas del dataset")
        self.geometry("480x520")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)

        header = ctk.CTkFrame(self, fg_color=AZUL_OSCURO, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Estadísticas del dataset", font=("Helvetica", 14, "bold"),
                     text_color="white").pack(padx=20, pady=14, anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        if not paises:
            ctk.CTkLabel(scroll, text="No hay datos cargados.",
                         text_color=TEXTO_MUTED).pack(pady=40)
            return

        stats = calcular_estadisticas(paises)
        self._construir_contenido(scroll, stats)

        ctk.CTkButton(
            self, text="Cerrar", fg_color=AZUL_OSCURO,
            hover_color=AZUL_MED, text_color="white",
            height=38, command=self.destroy
        ).pack(padx=20, pady=(0, 16), fill="x")

    def _seccion(self, parent, titulo):
        """Crea un frame de sección con título."""
        f = ctk.CTkFrame(parent, fg_color=BG_SEC, corner_radius=8)
        f.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(f, text=titulo, font=("Helvetica", 12, "bold"),
                     text_color=AZUL_OSCURO).pack(anchor="w", padx=14, pady=(10, 6))
        return f

    def _fila(self, parent, label, valor):
        """Agrega una fila etiqueta-valor dentro de una sección."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(row, text=label, font=("Helvetica", 12),
                     text_color=TEXTO_MUTED, width=200, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=valor, font=("Helvetica", 12, "bold"),
                     text_color=TEXTO, anchor="w").pack(side="left")

    def _construir_contenido(self, scroll, stats):
        """Construye todas las secciones de estadísticas."""
        # General
        sec = self._seccion(scroll, "General")
        self._fila(sec, "Total de países:", str(stats["total"]))
        self._fila(sec, "Promedio de población:",
                   formatear_numero(stats["prom_pob"]) + " hab.")
        self._fila(sec, "Promedio de superficie:",
                   formatear_numero(stats["prom_sup"]) + " km²")
        ctk.CTkFrame(sec, height=10, fg_color="transparent").pack()

        # Población
        sec2 = self._seccion(scroll, "Población")
        mp   = stats["mayor_pob"]
        menp = stats["menor_pob"]
        self._fila(sec2, "Mayor población:",
                   f"{mp['nombre']} ({formatear_numero(mp['poblacion'])} hab.)")
        self._fila(sec2, "Menor población:",
                   f"{menp['nombre']} ({formatear_numero(menp['poblacion'])} hab.)")
        ctk.CTkFrame(sec2, height=10, fg_color="transparent").pack()

        # Superficie
        sec3 = self._seccion(scroll, "Superficie")
        ms   = stats["mayor_sup"]
        mens = stats["menor_sup"]
        self._fila(sec3, "Mayor superficie:",
                   f"{ms['nombre']} ({formatear_numero(ms['superficie'])} km²)")
        self._fila(sec3, "Menor superficie:",
                   f"{mens['nombre']} ({formatear_numero(mens['superficie'])} km²)")
        ctk.CTkFrame(sec3, height=10, fg_color="transparent").pack()

        # Por continente
        sec4 = self._seccion(scroll, "Países por continente")
        items_cont = list(stats["por_continente"].items())
        items_cont = ordenar_items_por_cantidad(items_cont)
        for cont, cant in items_cont:
            self._fila(sec4, cont + ":", f"{cant} país{'es' if cant > 1 else ''}")
        ctk.CTkFrame(sec4, height=10, fg_color="transparent").pack()


# ─────────────────────────────────────────────
#  VENTANA: ORDENAR
# ─────────────────────────────────────────────

class VentanaOrdenar(ctk.CTkToplevel):
    """
    Ventana modal para seleccionar el campo y dirección de ordenamiento.

    Parámetros:
        parent: Ventana padre.
        orden_actual (dict): {"campo": str, "ascendente": bool}.
        callback (callable): Recibe (campo, ascendente).
    """

    def __init__(self, parent, orden_actual, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Ordenar países")
        self.geometry("320x340")
        self.resizable(False, True)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)

        header = ctk.CTkFrame(self, fg_color=AZUL_OSCURO, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Ordenar países", font=("Helvetica", 14, "bold"),
                     text_color="white").pack(padx=20, pady=14, anchor="w")

        form = ctk.CTkFrame(self, fg_color=BG_MAIN)
        form.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(form, text="Ordenar por", font=("Helvetica", 12, "bold"),
                     text_color=TEXTO).pack(anchor="w", pady=(0, 6))
        self.campo_var = ctk.StringVar(value=orden_actual.get("campo", "nombre"))
        for texto, valor in [("Nombre", "nombre"), ("Población", "poblacion"),
                              ("Superficie", "superficie")]:
            ctk.CTkRadioButton(
                form, text=texto, variable=self.campo_var, value=valor,
                font=("Helvetica", 12), text_color=TEXTO, fg_color=AZUL_OSCURO
            ).pack(anchor="w", pady=2)

        ctk.CTkLabel(form, text="Dirección", font=("Helvetica", 12, "bold"),
                     text_color=TEXTO).pack(anchor="w", pady=(12, 6))
        self.dir_var = ctk.StringVar(
            value="asc" if orden_actual.get("ascendente", True) else "desc"
        )
        row_dir = ctk.CTkFrame(form, fg_color="transparent")
        row_dir.pack(anchor="w")
        ctk.CTkRadioButton(
            row_dir, text="Ascendente ↑", variable=self.dir_var, value="asc",
            font=("Helvetica", 12), text_color=TEXTO, fg_color=AZUL_OSCURO
        ).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(
            row_dir, text="Descendente ↓", variable=self.dir_var, value="desc",
            font=("Helvetica", 12), text_color=TEXTO, fg_color=AZUL_OSCURO
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkButton(
            btn_frame, text="Cancelar", fg_color="transparent",
            border_width=1, border_color=BORDE, text_color=TEXTO,
            hover_color=BG_SEC, height=36, command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            btn_frame, text="Aplicar orden", fg_color=AZUL_OSCURO,
            hover_color=AZUL_MED, text_color="white",
            height=36, command=self._aplicar
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _aplicar(self):
        self.callback(self.campo_var.get(), self.dir_var.get() == "asc")
        self.destroy()


# ─────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────

class App(ctk.CTk):
    """
    Ventana principal de GeoData.

    Gestiona el estado de la aplicación (lista de países, filtros,
    orden, búsqueda) y coordina todos los subcomponentes visuales.
    """

    def __init__(self):
        super().__init__()
        self.title("GeoData — Gestión de Países")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(fg_color=BG_MAIN)

        # Estado de la aplicación
        self.paises = []
        self.csv_ruta = obtener_ruta_csv_default()
        self.filtros = {
            "continente": "Todos",
            "pob_min": None, "pob_max": None,
            "sup_min": None, "sup_max": None,
        }
        self.orden = {"campo": "nombre", "ascendente": True}
        self.busqueda = ""

        self._construir_ui()
        self._cargar_inicial()

    # ── CONSTRUCCIÓN DE LA INTERFAZ ──────────────

    def _construir_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._construir_sidebar()
        self._construir_main()

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=AZUL_OSCURO, corner_radius=0, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)

        # Logo / encabezado
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(18, 12))
        ctk.CTkLabel(logo_frame, text="🌍  GeoData", font=("Helvetica", 15, "bold"),
                        text_color="white").pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="Gestión de Países", font=("Helvetica", 10),
                        text_color=AZUL_CLARO).pack(anchor="w")

        sep = ctk.CTkFrame(sidebar, fg_color="white", height=1, bg_color=AZUL_OSCURO)
        sep.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))
        ctk.CTkFrame(sep, fg_color="#1A5A94", height=1).pack(fill="x")

        # Navegación
        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)

        self.nav_buttons = {}
        secciones = [
            ("Principal", [
                ("paises",       "📋  Países",       self._ver_paises),
                ("buscar",       "🔍  Buscar",        self._ver_buscar),
                ("filtros",      "⚙️  Filtros",       self._abrir_filtros),
            ]),
            ("Herramientas", [
                ("ordenar",      "↕️  Ordenar",       self._abrir_ordenar),
                ("estadisticas", "📊  Estadísticas",  self._ver_estadisticas),
            ]),
            ("Datos", [
                ("importar",     "📂  Importar CSV",  self._importar_csv),
                ("exportar",     "💾  Exportar CSV",  self._exportar_csv),
            ]),
        ]

        for seccion_titulo, items in secciones:
            ctk.CTkLabel(nav, text=seccion_titulo.upper(), font=("Helvetica", 9),
                            text_color=AZUL_CLARO).pack(anchor="w", padx=6, pady=(10, 2))
            for key, texto, comando in items:
                btn = ctk.CTkButton(
                    nav, text=texto, anchor="w", font=("Helvetica", 12),
                    fg_color="transparent", hover_color="#1A5A94",
                    text_color="white", height=34, corner_radius=6, command=comando
                )
                btn.pack(fill="x", pady=1)
                self.nav_buttons[key] = btn

        # Footer
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(footer, text="UTN — Programación 1", font=("Helvetica", 9),
                        text_color=AZUL_CLARO).pack(anchor="w")

    def _construir_main(self):
        self.main = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # Topbar
        self.topbar = ctk.CTkFrame(self.main, fg_color=BG_MAIN, height=56, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_columnconfigure(1, weight=1)
        self.topbar.grid_propagate(False)

        self.lbl_titulo = ctk.CTkLabel(
            self.topbar, text="Listado de países",
            font=("Helvetica", 15, "bold"), text_color=TEXTO
        )
        self.lbl_titulo.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        self.topbar_btns = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.topbar_btns.grid(row=0, column=2, padx=12, sticky="e")

        ctk.CTkButton(
            self.topbar_btns, text="↕ Ordenar", height=32,
            font=("Helvetica", 12), fg_color="transparent",
            border_width=1, border_color=BORDE, text_color=TEXTO,
            hover_color=BG_SEC, command=self._abrir_ordenar
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            self.topbar_btns, text="+ Agregar país", height=32,
            font=("Helvetica", 12), fg_color=AZUL_OSCURO,
            hover_color=AZUL_MED, text_color="white",
            command=self._agregar_pais
        ).pack(side="left", padx=4)

        sep_top = ctk.CTkFrame(self.main, fg_color=BORDE, height=1)
        sep_top.grid(row=1, column=0, sticky="ew")

        # Panel central
        self.panel = ctk.CTkFrame(self.main, fg_color=BG_MAIN, corner_radius=0)
        self.panel.grid(row=2, column=0, sticky="nsew")
        self.panel.grid_rowconfigure(3, weight=1)
        self.panel.grid_columnconfigure(0, weight=1)

        self._construir_stat_cards()
        self._construir_searchbar()
        self._construir_filtros_chips()
        self._construir_tabla()

    def _construir_stat_cards(self):
        self.stats_frame = ctk.CTkFrame(self.panel, fg_color=BG_MAIN)
        self.stats_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1)

        self.stat_cards = {}
        configs = [
            ("total",       "Total países",  "0",  "en el dataset"),
            ("mayor_pob",   "Mayor pob.",     "—",  ""),
            ("mayor_sup",   "Mayor sup.",     "—",  ""),
            ("continentes", "Continentes",    "0",  "representados"),
        ]
        for i, (key, label, val, sub) in enumerate(configs):
            card = ctk.CTkFrame(self.stats_frame, fg_color=BG_SEC, corner_radius=8)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            ctk.CTkLabel(card, text=label, font=("Helvetica", 10),
                            text_color=TEXTO_MUTED).pack(anchor="w", padx=12, pady=(10, 2))
            lbl_val = ctk.CTkLabel(card, text=val,
                                font=("Helvetica", 18, "bold"), text_color=TEXTO)
            lbl_val.pack(anchor="w", padx=12)
            lbl_sub = ctk.CTkLabel(card, text=sub,
                                font=("Helvetica", 10), text_color=TEXTO_MUTED)
            lbl_sub.pack(anchor="w", padx=12, pady=(0, 10))
            self.stat_cards[key] = (lbl_val, lbl_sub)

    def _construir_searchbar(self):
        search_frame = ctk.CTkFrame(self.panel, fg_color=BG_SEC, corner_radius=0, height=42)
        search_frame.grid(row=1, column=0, sticky="ew")
        search_frame.grid_propagate(False)
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍",
                    font=("Helvetica", 14)).grid(row=0, column=0, padx=(14, 6), pady=10)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_busqueda)
        self.search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var, height=30,
            placeholder_text="Buscar por nombre (parcial o exacto)...",
            font=("Helvetica", 12), fg_color="transparent",
            border_width=0, text_color=TEXTO
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 14))

    def _construir_filtros_chips(self):
        self.chips_frame = ctk.CTkFrame(self.panel, fg_color=BG_MAIN, height=38)
        self.chips_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        ctk.CTkLabel(self.chips_frame, text="Continente:", font=("Helvetica", 11),
                        text_color=TEXTO_MUTED).pack(side="left", padx=(4, 8))

        self.chip_buttons = {}
        opciones = ["Todos"] + CONTINENTES
        for opcion in opciones:
            btn = ctk.CTkButton(
                self.chips_frame, text=opcion, height=26, font=("Helvetica", 11),
                corner_radius=13, fg_color=BG_SEC, border_width=1,
                border_color=BORDE, text_color=TEXTO_MUTED, hover_color=AZUL_CLARO,
                command=self._hacer_filtro_chip(opcion)
            )
            btn.pack(side="left", padx=2)
            self.chip_buttons[opcion] = btn

        ctk.CTkButton(
            self.chips_frame, text="⚙ Rangos", height=26, font=("Helvetica", 11),
            corner_radius=13, fg_color=BG_SEC, border_width=1, border_color=BORDE,
            text_color=TEXTO_MUTED, hover_color=AZUL_CLARO, command=self._abrir_filtros
        ).pack(side="right", padx=4)

        self.lbl_filtro_activo = ctk.CTkLabel(
            self.chips_frame, text="", font=("Helvetica", 10), text_color=AZUL_MED
        )
        self.lbl_filtro_activo.pack(side="right", padx=4)
        self._actualizar_chips("Todos")

    def _construir_tabla(self):
        tabla_frame = ctk.CTkFrame(self.panel, fg_color=BG_MAIN, corner_radius=0)
        tabla_frame.grid(row=3, column=0, sticky="nsew", padx=0, pady=0)
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        # Estilo ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                            background=BG_MAIN, foreground=TEXTO,
                            rowheight=36, fieldbackground=BG_MAIN,
                            borderwidth=0, font=("Helvetica", 12))
        style.configure("Custom.Treeview.Heading",
                            background=BG_SEC, foreground=TEXTO_MUTED,
                            font=("Helvetica", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Custom.Treeview",
                    background=[("selected", "#DDE9F5")],
                    foreground=[("selected", TEXTO)])
        style.map("Custom.Treeview.Heading",
                    background=[("active", BORDE)])

        columnas = ("nombre", "continente", "poblacion", "superficie")
        self.tabla = ttk.Treeview(
            tabla_frame, columns=columnas, show="headings",
            style="Custom.Treeview", selectmode="browse"
        )

        self.tabla.heading("nombre",     text="Nombre ⇅",          anchor="w",
                           command=self._ordenar_por_nombre)
        self.tabla.heading("continente", text="Continente",         anchor="w")
        self.tabla.heading("poblacion",  text="Población ⇅",        anchor="e",
                           command=self._ordenar_por_poblacion)
        self.tabla.heading("superficie", text="Superficie km² ⇅",   anchor="e",
                           command=self._ordenar_por_superficie)

        self.tabla.column("nombre",     width=200, minwidth=120, anchor="w")
        self.tabla.column("continente", width=110, minwidth=90,  anchor="w")
        self.tabla.column("poblacion",  width=160, minwidth=100, anchor="e")
        self.tabla.column("superficie", width=160, minwidth=100, anchor="e")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

        # Menú contextual
        self.menu_ctx = tk.Menu(self, tearoff=0)
        self.menu_ctx.add_command(label="✏️  Editar",    command=self._editar_pais)
        self.menu_ctx.add_command(label="🗑️  Eliminar",  command=self._eliminar_pais)
        self.tabla.bind("<Button-3>",        self._mostrar_menu_ctx)
        self.tabla.bind("<Double-Button-1>", self._on_doble_click)

        # Barra inferior de estado
        self.bottom_bar = ctk.CTkFrame(self.panel, fg_color=BG_SEC, height=32, corner_radius=0)
        self.bottom_bar.grid(row=4, column=0, sticky="ew")
        self.bottom_bar.grid_propagate(False)
        self.lbl_conteo = ctk.CTkLabel(
            self.bottom_bar, text="", font=("Helvetica", 11), text_color=TEXTO_MUTED
        )
        self.lbl_conteo.pack(side="left", padx=14, pady=6)
        self.lbl_orden_info = ctk.CTkLabel(
            self.bottom_bar, text="", font=("Helvetica", 11), text_color=TEXTO_MUTED
        )
        self.lbl_orden_info.pack(side="right", padx=14, pady=6)

    # ── LÓGICA DE CARGA Y VISUALIZACIÓN ──────────

    def _cargar_inicial(self):
        """
        Carga el CSV por defecto al iniciar la aplicación.
        Si el archivo no existe, arranca con dataset vacío sin mostrar ningún error.
        Solo muestra error si el archivo existe pero tiene formato incorrecto.
        """
        import os
        if not os.path.exists(self.csv_ruta):
            # Archivo no encontrado: arrancar vacío, sin mensajes
            self.paises = []
            self._refrescar_todo()
            return

        paises, errores = cargar_csv(self.csv_ruta)
        if paises is None:
            # El archivo existe pero tiene un problema de formato grave
            messagebox.showerror("Error al cargar CSV", str(errores))
            self.paises = []
        else:
            self.paises = paises
            if errores:
                messagebox.showwarning(
                    "Advertencias al cargar",
                    "Se omitieron algunas filas:\n" + "\n".join(errores)
                )
        self._refrescar_todo()

    def _refrescar_todo(self):
        """Actualiza estadísticas y tabla tras cualquier cambio en los datos."""
        self._actualizar_stats()
        self._actualizar_tabla()

    def _actualizar_stats(self):
        """Actualiza las tarjetas de estadísticas de la topbar."""
        stats = calcular_estadisticas(self.paises)
        if not stats:
            for _key, (lbl_v, lbl_s) in self.stat_cards.items():
                lbl_v.configure(text="—")
                lbl_s.configure(text="")
            return

        self.stat_cards["total"][0].configure(text=str(stats["total"]))
        self.stat_cards["total"][1].configure(text="en el dataset")

        mp = stats["mayor_pob"]
        self.stat_cards["mayor_pob"][0].configure(text=mp["nombre"])
        self.stat_cards["mayor_pob"][1].configure(
            text=f'{formatear_numero(mp["poblacion"])} hab.'
        )

        ms = stats["mayor_sup"]
        self.stat_cards["mayor_sup"][0].configure(text=ms["nombre"])
        self.stat_cards["mayor_sup"][1].configure(
            text=f'{formatear_numero(ms["superficie"])} km²'
        )

        n_cont = len(stats["por_continente"])
        self.stat_cards["continentes"][0].configure(text=str(n_cont))
        self.stat_cards["continentes"][1].configure(text="representados")

    def _aplicar_filtros_y_orden(self):
        """Aplica todos los filtros activos + búsqueda + orden y devuelve la lista."""
        resultado = filtrar_paises(
            self.paises,
            continente=self.filtros["continente"],
            pob_min=self.filtros["pob_min"],
            pob_max=self.filtros["pob_max"],
            sup_min=self.filtros["sup_min"],
            sup_max=self.filtros["sup_max"],
        )
        if self.busqueda:
            resultado = buscar_paises(resultado, self.busqueda)
        resultado = ordenar_paises(resultado, self.orden["campo"], self.orden["ascendente"])
        return resultado

    def _actualizar_tabla(self):
        """Limpia y repobla el Treeview con los datos filtrados/ordenados."""
        self.tabla.delete(*self.tabla.get_children())
        datos = self._aplicar_filtros_y_orden()

        for p in datos:
            self.tabla.insert("", "end", values=(
                p["nombre"],
                p["continente"],
                formatear_numero(p["poblacion"]),
                formatear_numero(p["superficie"]),
            ))

        total     = len(self.paises)
        mostrados = len(datos)
        if mostrados != total:
            self.lbl_conteo.configure(text=f"Mostrando {mostrados} de {total} países")
        else:
            self.lbl_conteo.configure(text=f"{total} países")

        dir_txt = "↑" if self.orden["ascendente"] else "↓"
        self.lbl_orden_info.configure(
            text=f"Orden: {self.orden['campo']} {dir_txt}"
        )
        self._actualizar_filtro_label()

    def _actualizar_filtro_label(self):
        """Muestra en la barra los rangos de filtro activos."""
        partes = []
        f = self.filtros
        if f["pob_min"] or f["pob_max"]:
            min_txt = formatear_numero(f["pob_min"]) if f["pob_min"] else "0"
            max_txt = formatear_numero(f["pob_max"]) if f["pob_max"] else "∞"
            partes.append(f"Pob: {min_txt} – {max_txt}")
        if f["sup_min"] or f["sup_max"]:
            min_txt = formatear_numero(f["sup_min"]) if f["sup_min"] else "0"
            max_txt = formatear_numero(f["sup_max"]) if f["sup_max"] else "∞"
            partes.append(f"Sup: {min_txt} – {max_txt}")
        self.lbl_filtro_activo.configure(
            text=("  " + " | ".join(partes)) if partes else ""
        )

    # ── ACCIONES DEL USUARIO ──────────────────────

    def _on_busqueda(self, *_args):
        """Callback del trace en el Entry de búsqueda."""
        self.busqueda = self.search_var.get()
        self._actualizar_tabla()

    def _on_doble_click(self, _evento):
        """Abre el editor al hacer doble clic en una fila."""
        self._editar_pais()

    def _hacer_filtro_chip(self, opcion):
        """
        Devuelve una función que filtra por el continente dado.
        Reemplaza el uso de lambda en los botones de chips.
        """
        def _filtrar():
            self._filtrar_continente(opcion)
        return _filtrar

    def _filtrar_continente(self, continente):
        self.filtros["continente"] = continente
        self._actualizar_chips(continente)
        self._actualizar_tabla()

    def _actualizar_chips(self, activo):
        """Resalta el chip del continente seleccionado."""
        for opcion, btn in self.chip_buttons.items():
            if opcion == activo:
                btn.configure(fg_color=AZUL_OSCURO, text_color="white",
                              border_color=AZUL_OSCURO)
            else:
                btn.configure(fg_color=BG_SEC, text_color=TEXTO_MUTED,
                              border_color=BORDE)

    def _ordenar_columna(self, campo):
        """Alterna dirección si el campo ya está activo, o cambia al nuevo campo."""
        if self.orden["campo"] == campo:
            self.orden["ascendente"] = not self.orden["ascendente"]
        else:
            self.orden["campo"] = campo
            self.orden["ascendente"] = True
        self._actualizar_tabla()

    def _ordenar_por_nombre(self):
        self._ordenar_columna("nombre")

    def _ordenar_por_poblacion(self):
        self._ordenar_columna("poblacion")

    def _ordenar_por_superficie(self):
        self._ordenar_columna("superficie")

    def _abrir_filtros(self):
        VentanaFiltros(self, self.filtros, self._aplicar_filtros_rango)

    def _aplicar_filtros_rango(self, filtros):
        self.filtros.update(filtros)
        self._actualizar_tabla()

    def _abrir_ordenar(self):
        VentanaOrdenar(self, self.orden, self._aplicar_orden)

    def _aplicar_orden(self, campo, ascendente):
        self.orden["campo"] = campo
        self.orden["ascendente"] = ascendente
        self._actualizar_tabla()

    def _ver_paises(self):
        self.lbl_titulo.configure(text="Listado de países")

    def _ver_buscar(self):
        self.search_entry.focus_set()

    def _ver_estadisticas(self):
        VentanaEstadisticas(self, self.paises)

    # ── CRUD ──────────────────────────────────────

    def _agregar_pais(self):
        VentanaPais(self, callback=self._guardar_nuevo_pais)

    def _guardar_nuevo_pais(self, pais, _original):
        """Agrega un país nuevo verificando que el nombre no esté duplicado."""
        if nombre_duplicado(self.paises, pais["nombre"]):
            messagebox.showerror(
                "Error", f"Ya existe un país con el nombre «{pais['nombre']}»."
            )
            return
        self.paises.append(pais)
        guardar_csv(self.paises, self.csv_ruta)
        self._refrescar_todo()

    def _get_pais_seleccionado(self):
        """Devuelve el dict del país seleccionado en la tabla, o None."""
        sel = self.tabla.selection()
        if not sel:
            return None
        valores = self.tabla.item(sel[0])["values"]
        nombre = valores[0]
        for p in self.paises:
            if p["nombre"] == nombre:
                return p
        return None

    def _editar_pais(self):
        pais = self._get_pais_seleccionado()
        if not pais:
            messagebox.showinfo("Info", "Seleccioná un país de la tabla primero.")
            return
        VentanaPais(self, pais=pais, callback=self._guardar_edicion)

    def _guardar_edicion(self, nuevo, original):
        """Actualiza un país existente, verificando nombre duplicado."""
        idx = None
        for i, p in enumerate(self.paises):
            if p["nombre"] == original["nombre"]:
                idx = i
                break
        if idx is None:
            return
        if nombre_duplicado(self.paises, nuevo["nombre"], excluir_idx=idx):
            messagebox.showerror(
                "Error", f"Ya existe un país con el nombre «{nuevo['nombre']}»."
            )
            return
        self.paises[idx] = nuevo
        guardar_csv(self.paises, self.csv_ruta)
        self._refrescar_todo()

    def _eliminar_pais(self):
        pais = self._get_pais_seleccionado()
        if not pais:
            messagebox.showinfo("Info", "Seleccioná un país de la tabla primero.")
            return
        ok = messagebox.askyesno(
            "Confirmar", f"¿Eliminás a «{pais['nombre']}» del dataset?"
        )
        if ok:
            paises_nuevos = []
            for p in self.paises:
                if p["nombre"] != pais["nombre"]:
                    paises_nuevos.append(p)
            self.paises = paises_nuevos
            guardar_csv(self.paises, self.csv_ruta)
            self._refrescar_todo()

    def _mostrar_menu_ctx(self, event):
        item = self.tabla.identify_row(event.y)
        if item:
            self.tabla.selection_set(item)
            try:
                self.menu_ctx.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu_ctx.grab_release()

    # ── IMPORTAR / EXPORTAR ───────────────────────

    def _importar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccioná un archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not ruta:
            return
        paises, errores = cargar_csv(ruta)
        if paises is None:
            messagebox.showerror("Error al importar", str(errores))
            return
        self.paises = paises
        self.csv_ruta = ruta
        if errores:
            messagebox.showwarning(
                "Advertencias al importar",
                f"Se cargaron {len(paises)} países con advertencias:\n" + "\n".join(errores)
            )
        else:
            messagebox.showinfo(
                "Importación exitosa", f"Se cargaron {len(paises)} países correctamente."
            )
        self._refrescar_todo()

    def _exportar_csv(self):
        if not self.paises:
            messagebox.showwarning("Sin datos", "No hay países para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar CSV",
            defaultextension=".csv",
            initialfile="paises_exportado.csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not ruta:
            return
        guardar_csv(self.paises, ruta)
        messagebox.showinfo("Exportación exitosa", f"Dataset guardado en:\n{ruta}")


# ─────────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
