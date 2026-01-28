import tkinter as tk
from tkinter import ttk
from typing import List, Optional

# Importamos lógica y formateador
from logica.inductores import (
    calcular_inductor_por_bandas,
    formatear_henrios,
    VALORES_SIGNIFICATIVOS_IND,
    MULTIPLICADORES_IND,
    TOLERANCIAS_IND
)
# Reutilizamos el mapeo de color a código hexadecimal
from .resistencia_colores import ResistenciaColoresFrame

class InductorColoresFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, on_back=None) -> None:
        super().__init__(master)
        # Inductores típicamente 4 bandas para este código
        self.num_bandas = 4
        self.band_colors: List[tk.StringVar] = []

        # --- Header ---
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        title = ttk.Label(header_frame, text=" Coil Calculadora: Código de Colores Inductores",
                          font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        title.pack(side=tk.LEFT)
        if on_back:
            try:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back, style="Secondary.TButton")
            except tk.TclError:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back)
            btn_back.pack(side=tk.RIGHT)

        # Contenedor principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- Panel de Selección de Bandas ---
        self.bands_panel = ttk.LabelFrame(main_frame, text=" Selección de Colores (4 Bandas)", padding=15) # Sin style
        self.bands_panel.pack(fill=tk.X, pady=(0, 15))

        # --- Canvas Previsualización ---
        canvas_frame = ttk.LabelFrame(main_frame, text=" Previsualización", padding=15) # Sin style
        canvas_frame.pack(fill=tk.X, pady=(0, 15))
        self.canvas = tk.Canvas(canvas_frame, height=120, bg="#ffffff", # Menor altura
                                highlightthickness=2, highlightbackground="#e0e0e0", relief="solid")
        self.canvas.pack(fill=tk.X, pady=10)
        # Usamos lambda para pasar self.band_colors en el momento de la llamada
        self.canvas.bind("<Configure>", lambda e: self._draw_inductor([v.get() for v in self.band_colors]))

        # --- Panel de Resultado ---
        result_frame = ttk.LabelFrame(main_frame, text="📊 Resultado del Cálculo", padding=20) # Sin style
        result_frame.pack(fill=tk.X)
        result_container = ttk.Frame(result_frame)
        result_container.pack(fill=tk.X)

        # Resultado principal (Inductancia)
        self.result_var = tk.StringVar(value="")
        result_label = ttk.Label(result_container, textvariable=self.result_var,
                                 font=("Segoe UI", 20, "bold"), foreground="#1a1a1a") # Sin style
        result_label.pack(pady=(0, 15))

        # Detalles (Tolerancia)
        details_frame = ttk.Frame(result_container)
        details_frame.pack(fill=tk.X)
        self.tolerance_value_var = tk.StringVar(value="")
        tolerance_label = ttk.Label(details_frame, text="Tolerancia:",
                                    font=("Segoe UI", 11, "bold"), foreground="#2c3e50")
        tolerance_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        tolerance_value_label = ttk.Label(details_frame, textvariable=self.tolerance_value_var,
                                          font=("Segoe UI", 11), foreground="#1a1a1a")
        tolerance_value_label.grid(row=0, column=1, sticky=tk.W)

        # Info adicional
        self.info_var = tk.StringVar(value="Seleccione los 4 colores.")
        info_label = ttk.Label(result_container, textvariable=self.info_var,
                               font=("Segoe UI", 10), foreground="#2c3e50", # Sin style
                               wraplength=600, justify=tk.CENTER)
        info_label.pack(pady=(15, 0))

        # Inicializar Comboboxes y primer cálculo/dibujo
        self._build_bands()
        self.after(10, self._update_result) # Forzar actualización inicial

    def _build_bands(self):
        """Crea los Combobox para las 4 bandas."""
        for child in self.bands_panel.winfo_children():
            child.destroy()
        self.band_colors.clear()

        # Roles fijos para 4 bandas: D1, D2, Multiplicador, Tolerancia
        roles = ["d", "d", "m", "t"]
        role_names = {"d": "Dígito", "m": "Multiplicador (µH)", "t": "Tolerancia"}

        for idx, role in enumerate(roles):
            var = tk.StringVar()
            self.band_colors.append(var)

            band_frame = ttk.Frame(self.bands_panel)
            band_frame.grid(row=0, column=idx, padx=10, pady=5, sticky="nsew")

            label = ttk.Label(band_frame, text=f"Banda {idx+1}\n({role_names[role]})",
                              font=("Segoe UI", 10, "bold"), justify=tk.CENTER)
            label.pack(pady=(0, 5))

            combo = ttk.Combobox(band_frame, textvariable=var, state="readonly", width=12)
            combo["values"] = self._colors_for_role(role)
            combo.bind("<<ComboboxSelected>>", self._update_result) # Sin lambda event

            # Intentar seleccionar un valor inicial común
            default_color = "marrón" if idx == 0 else "negro" if idx < 2 else "negro" if idx == 2 else "oro"
            if default_color in combo["values"]:
                 combo.set(default_color)
            else:
                 combo.current(0) # O el primer color disponible

            combo.pack()
            self.bands_panel.grid_columnconfigure(idx, weight=1)

    def _colors_for_role(self, role: str) -> List[str]:
        """Devuelve la lista de colores válidos para un rol de banda de inductor."""
        if role == "d":
            return list(VALORES_SIGNIFICATIVOS_IND.keys())
        if role == "m":
            return list(MULTIPLICADORES_IND.keys())
        if role == "t":
            # Añadir opción 'ninguno' si es relevante para el 20%
            return list(TOLERANCIAS_IND.keys()) # Incluye 'ninguno' si está en el dict
        return []

    def _update_result(self, event=None):
        """Recalcula y actualiza la interfaz."""
        bands = [v.get() for v in self.band_colors]

        if not all(bands): # Si alguna banda está vacía
            self.result_var.set("")
            self.tolerance_value_var.set("")
            self.info_var.set("Seleccione los 4 colores.")
            self._draw_inductor(bands) # Dibujar con lo que haya
            return

        try:
            valor_h, tol = calcular_inductor_por_bandas(bands)
            self.result_var.set(formatear_henrios(valor_h))

            if tol is not None:
                self.tolerance_value_var.set(f"±{tol}%")
            else:
                self.tolerance_value_var.set("N/A") # O dejar vacío

            # Info adicional
            info_parts = ["Inductor 4 bandas (µH): D1 D2 × Multiplicador ± Tolerancia"]
            # Podríamos añadir clasificación µH, mH, H aquí
            self.info_var.set(" • ".join(info_parts))
            self._draw_inductor(bands)

        except ValueError as e:
            self.result_var.set("Error")
            self.tolerance_value_var.set("")
            self.info_var.set(str(e))
            self._draw_inductor(bands) # Dibujar igual para mostrar colores seleccionados

    def _draw_inductor(self, bands: List[Optional[str]]):
        """Dibuja una representación simple de un inductor axial con bandas."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 300 # Valor por defecto
        h = self.canvas.winfo_height() or 120
        margin = 40
        body_w = w - 2 * margin
        body_h = h * 0.6 # Cuerpo más grueso
        y = h // 2

        # Terminales
        self.canvas.create_line(margin - 30, y, margin, y, width=4, fill="#666")
        self.canvas.create_line(w - margin, y, w - margin + 30, y, width=4, fill="#666")

        # Cuerpo (grisáceo/azul claro típico)
        self.canvas.create_rectangle(margin, y - body_h // 2, margin + body_w, y + body_h // 2,
                                     fill="#dbe4ee", outline="#adb5bd", width=2)

        # Bandas (4 fijas)
        num_expected_bands = 4
        gap = body_w / (num_expected_bands + 1)
        # Usamos _tk_color de ResistenciaColoresFrame importado
        tk_color_func = ResistenciaColoresFrame._tk_color

        for i in range(num_expected_bands):
            color_name = bands[i] if i < len(bands) and bands[i] else "gris" # Color por defecto si falta
            x = margin + (i + 1) * gap
            band_color_hex = tk_color_func(self, color_name) # Pasamos 'self' dummy

            # Dibujar banda
            self.canvas.create_rectangle(x - 8, y - body_h // 2, x + 8, y + body_h // 2,
                                         fill=band_color_hex, outline="#333", width=1)
