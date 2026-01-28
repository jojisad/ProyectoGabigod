import tkinter as tk
from tkinter import ttk
from typing import Optional

# Importamos la lógica y el formateador
from logica.divisor_voltaje import calcular_divisor_voltaje
from logica.ley_ohm import formatear_valor # Reutilizamos formateador

class DivisorVoltajeFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, on_back=None) -> None:
        super().__init__(master)

        # Variables para entradas y resultado
        self.vin_var = tk.StringVar()
        self.r1_var = tk.StringVar()
        self.r2_var = tk.StringVar()
        self.vout_var = tk.StringVar()
        self.info_var = tk.StringVar(value="Ingrese Vin, R1 y R2 para calcular Vout.")

        # --- Header ---
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        title = ttk.Label(header_frame, text="🔗 Calculadora: Divisor de Voltaje",
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

        # --- Panel de Entrada ---
        input_frame = ttk.LabelFrame(main_frame, text="🔢 Entrada de Datos", padding=15) # Sin style
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        # Fila Voltaje Entrada
        ttk.Label(input_frame, text="Voltaje Entrada (Vin):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        vin_entry = ttk.Entry(input_frame, textvariable=self.vin_var, font=("Segoe UI", 12))
        vin_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        vin_entry.bind("<KeyRelease>", self._actualizar_calculo)

        # Fila R1
        ttk.Label(input_frame, text="Resistencia 1 (R1 Ω):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        r1_entry = ttk.Entry(input_frame, textvariable=self.r1_var, font=("Segoe UI", 12))
        r1_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        r1_entry.bind("<KeyRelease>", self._actualizar_calculo)

        # Fila R2
        ttk.Label(input_frame, text="Resistencia 2 (R2 Ω):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        r2_entry = ttk.Entry(input_frame, textvariable=self.r2_var, font=("Segoe UI", 12))
        r2_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        r2_entry.bind("<KeyRelease>", self._actualizar_calculo)

        # Botón Limpiar
        try:
            clear_button = ttk.Button(input_frame, text="Limpiar", command=self._limpiar_campos, style="Secondary.TButton")
        except tk.TclError:
            clear_button = ttk.Button(input_frame, text="Limpiar", command=self._limpiar_campos)
        clear_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # --- Panel de Resultado ---
        result_frame = ttk.LabelFrame(main_frame, text="📊 Voltaje de Salida (Vout)", padding=20) # Sin style
        result_frame.pack(fill=tk.X)

        # Resultado Vout
        result_label = ttk.Label(result_frame, textvariable=self.vout_var,
                                 font=("Segoe UI", 18, "bold"), foreground="#2c3e50") # Sin style
        result_label.pack(pady=(0, 10))

        # Info
        info_label = ttk.Label(result_frame, textvariable=self.info_var,
                               font=("Segoe UI", 10), foreground="#7f8c8d", # Sin style
                               wraplength=600, justify=tk.CENTER)
        info_label.pack()

    def _parse_float(self, value_str: str) -> Optional[float]:
        """Convierte string a float, o None si inválido/vacío."""
        if not value_str.strip(): return None
        try:
            return float(value_str.strip().replace(',', '.'))
        except ValueError:
            return None

    def _actualizar_calculo(self, event=None):
        """Intenta calcular Vout basado en las entradas."""
        vin_str = self.vin_var.get()
        r1_str = self.r1_var.get()
        r2_str = self.r2_var.get()

        vin = self._parse_float(vin_str)
        r1 = self._parse_float(r1_str)
        r2 = self._parse_float(r2_str)

        # Contar campos con texto y campos con números válidos
        campos_con_texto = sum(1 for txt in [vin_str, r1_str, r2_str] if txt.strip())
        valores_validos = sum(1 for val in [vin, r1, r2] if val is not None)

        # Error si hay texto no numérico
        if campos_con_texto > 0 and valores_validos < campos_con_texto:
            self.vout_var.set("Error")
            self.info_var.set("Por favor, ingrese solo números válidos.")
            return

        # Calcular solo si tenemos los 3 valores
        if valores_validos == 3:
            try:
                # Asegurarnos de pasar floats válidos a la lógica
                if vin is not None and r1 is not None and r2 is not None:
                    vout_calc = calcular_divisor_voltaje(vin, r1, r2)
                    self.vout_var.set(f"Vout = {formatear_valor(vout_calc, 'V')}")
                    self.info_var.set(f"Calculado con Vin={formatear_valor(vin, 'V')}, R1={formatear_valor(r1, 'Ω')}, R2={formatear_valor(r2, 'Ω')}")
                else:
                     # Esto no debería pasar si valores_validos == 3
                     raise ValueError("Error interno al obtener valores.")
            except ValueError as e:
                self.vout_var.set("Error")
                self.info_var.set(str(e))
        else:
            self.vout_var.set("")
            self.info_var.set("Ingrese Vin, R1 y R2 para calcular Vout.")

    def _limpiar_campos(self):
        """Borra entradas y resultado."""
        self.vin_var.set("")
        self.r1_var.set("")
        self.r2_var.set("")
        self.vout_var.set("")
        self.info_var.set("Ingrese Vin, R1 y R2 para calcular Vout.")
