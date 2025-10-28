import tkinter as tk
from tkinter import ttk
from typing import Optional

# Importamos lógica y formateador
from logica.filtros_simples import (
    calcular_fc_filtro_rc,
    calcular_fc_filtro_rl,
    formatear_valor # Reutilizado via filtros_simples.py
)

class FiltrosSimplesFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, on_back=None) -> None:
        super().__init__(master)

        # --- Header ---
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        title = ttk.Label(header_frame, text=" Fc Calculadora: Frecuencia Corte Filtros RC/RL",
                          font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        title.pack(side=tk.LEFT)
        if on_back:
            try:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back, style="Secondary.TButton")
            except tk.TclError:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back)
            btn_back.pack(side=tk.RIGHT)

        # Contenedor principal con Notebook para RC y RL
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # <<< CORRECCIÓN: Inicializar diccionarios ANTES de crear las pestañas >>>
        # Variables para almacenar referencias a widgets
        self.entradas = {}
        self.resultados = {}
        self.infos = {}
        # <<< FIN CORRECCIÓN >>>

        # --- Crear Pestaña Filtro RC ---
        self.tab_rc = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_rc, text=' Filtro RC (Fc) ')
        # Ahora self.entradas, etc., existen cuando se llama a esta función
        self._crear_interfaz_filtro(self.tab_rc, tipo='rc')

        # --- Crear Pestaña Filtro RL ---
        self.tab_rl = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_rl, text=' Filtro RL (Fc) ')
        # Ahora self.entradas, etc., existen cuando se llama a esta función
        self._crear_interfaz_filtro(self.tab_rl, tipo='rl')


    def _crear_interfaz_filtro(self, parent_frame: ttk.Frame, tipo: str):
        """Crea la interfaz de entrada y resultado para Filtro RC o RL."""

        # Variables específicas para esta pestaña
        r_var = tk.StringVar()
        comp_var = tk.StringVar() # Para C o L
        resultado_var = tk.StringVar()
        info_var = tk.StringVar(value="Ingrese Resistencia y Valor del Componente.")

        # Guardar referencias
        self.entradas[tipo] = {'r': r_var, 'comp': comp_var}
        self.resultados[tipo] = resultado_var
        self.infos[tipo] = info_var

        # --- Panel de Entrada ---
        input_frame = ttk.LabelFrame(parent_frame, text="🔢 Entrada de Datos", padding=15) # Sin style
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        # Resistencia
        ttk.Label(input_frame, text="Resistencia (Ω):", font=("Segoe UI", 11, "bold"), foreground="#495057").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        r_entry = ttk.Entry(input_frame, textvariable=r_var, font=("Segoe UI", 12))
        r_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        r_entry.bind("<KeyRelease>", lambda e, t=tipo: self._actualizar_calculo(t))

        # Componente (Capacitor o Inductor)
        label_texto = "Capacitancia (F):" if tipo == 'rc' else "Inductancia (H):"
        ttk.Label(input_frame, text=label_texto, font=("Segoe UI", 11, "bold"), foreground="#495057").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        comp_entry = ttk.Entry(input_frame, textvariable=comp_var, font=("Segoe UI", 12))
        comp_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        comp_entry.bind("<KeyRelease>", lambda e, t=tipo: self._actualizar_calculo(t))

        # Botón Limpiar
        clear_button = ttk.Button(input_frame, text="Limpiar",
                                  command=lambda t=tipo: self._limpiar_campos(t))
        try: clear_button.configure(style="Secondary.TButton")
        except tk.TclError: pass
        clear_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # --- Panel de Resultado ---
        result_frame = ttk.LabelFrame(parent_frame, text="📊 Resultado", padding=20) # Sin style
        result_frame.pack(fill=tk.X)

        result_label = ttk.Label(result_frame, textvariable=resultado_var,
                                 font=("Segoe UI", 18, "bold"), foreground="#2c3e50") # Sin style
        result_label.pack(pady=(0, 10))

        info_label = ttk.Label(result_frame, textvariable=info_var,
                               font=("Segoe UI", 10), foreground="#7f8c8d", # Sin style
                               wraplength=600, justify=tk.CENTER)
        info_label.pack()

    def _parse_float(self, value_str: str) -> Optional[float]:
        """Convierte string a float, devolviendo None si es inválido/vacío."""
        if not value_str.strip(): return None
        try: return float(value_str.strip().replace(',', '.'))
        except ValueError: return None

    def _actualizar_calculo(self, tipo: str, event=None):
        """Calcula la Frecuencia de Corte para la pestaña activa."""
        try:
            r_var = self.entradas[tipo]['r']
            comp_var = self.entradas[tipo]['comp']
            resultado_var = self.resultados[tipo]
            info_var = self.infos[tipo]

            r_str = r_var.get()
            comp_str = comp_var.get()

            r = self._parse_float(r_str)
            comp = self._parse_float(comp_str)

            # Validar texto inválido
            campos_con_texto = sum(1 for txt in [r_str, comp_str] if txt.strip())
            valores_validos = sum(1 for val in [r, comp] if val is not None)

            if campos_con_texto > valores_validos:
                 resultado_var.set("Error")
                 info_var.set("Por favor, ingrese solo números válidos.")
                 return

            if r is not None and comp is not None:
                try:
                    if tipo == 'rc':
                        fc = calcular_fc_filtro_rc(r, comp)
                        formula = "Fc = 1 / (2 * π * R * C)"
                        comp_unidad = "F"
                    else: # tipo == 'rl'
                        fc = calcular_fc_filtro_rl(r, comp)
                        formula = "Fc = R / (2 * π * L)"
                        comp_unidad = "H"

                    resultado = formatear_valor(fc, 'Hz') # Usar formateador para Hz
                    resultado_var.set(f"Frecuencia Corte (Fc) = {resultado}")
                    info_var.set(f"Calculado con R={formatear_valor(r, 'Ω')} y {'C' if tipo=='rc' else 'L'}={formatear_valor(comp, comp_unidad)}. Fórmula: {formula}")

                except ValueError as e:
                    resultado_var.set("Error")
                    info_var.set(str(e))
            else:
                resultado_var.set("")
                info_var.set("Ingrese Resistencia y Valor del Componente.")

        except KeyError:
             print(f"Error interno: tipo de filtro '{tipo}' no reconocido.")
        except Exception as e:
            try:
                self.resultados[tipo].set("Error")
                self.infos[tipo].set(f"Error inesperado: {e}")
            except KeyError: pass # Evitar error si falla al mostrar error

    def _limpiar_campos(self, tipo: str):
        """Limpia los campos de la pestaña especificada."""
        try:
            self.entradas[tipo]['r'].set("")
            self.entradas[tipo]['comp'].set("")
            self.resultados[tipo].set("")
            self.infos[tipo].set("Ingrese Resistencia y Valor del Componente.")
        except KeyError: pass # Evitar error si el tipo es incorrecto


