import tkinter as tk
from tkinter import ttk
from typing import Optional

# Importamos lógica y formateador
from logica.reactancia import (
    calcular_reactancia_capacitiva,
    calcular_reactancia_inductiva,
    formatear_valor # Reutilizado de ley_ohm via reactancia.py
)

class ReactanciaFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, on_back=None) -> None:
        super().__init__(master)

        # --- Header ---
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        title = ttk.Label(header_frame, text=" Z Calculadora: Reactancia (Xc y Xl)",
                          font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        title.pack(side=tk.LEFT)
        if on_back:
            # Usamos try-except por si el estilo Secondary.TButton falla
            try:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back, style="Secondary.TButton")
            except tk.TclError:
                btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back)
            btn_back.pack(side=tk.RIGHT)

        # Variables para almacenar referencias a widgets (para _actualizar_calculo)
        self.entradas = {}
        self.resultados = {}
        self.infos = {}

        # Contenedor principal con Notebook para Xc y Xl
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # --- Crear Pestaña Xc ---
        self.tab_xc = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_xc, text=' Reactancia Capacitiva (Xc) ')
        self._crear_interfaz_reactancia(self.tab_xc, tipo='capacitiva')

        # --- Crear Pestaña Xl ---
        self.tab_xl = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_xl, text=' Reactancia Inductiva (Xl) ')
        self._crear_interfaz_reactancia(self.tab_xl, tipo='inductiva')

        # Actualizar cálculo inicial (puede que no haya nada que calcular)
        # self._actualizar_calculo() # Mejor no llamar aquí, esperar entrada

    def _crear_interfaz_reactancia(self, parent_frame: ttk.Frame, tipo: str):
        """Crea la interfaz de entrada y resultado para Xc o Xl."""

        # Variables específicas para esta pestaña
        freq_var = tk.StringVar()
        comp_var = tk.StringVar() # Para Capacitancia o Inductancia
        resultado_var = tk.StringVar()
        info_var = tk.StringVar(value="Ingrese Frecuencia y Valor del Componente.")

        # Guardar referencias para acceso posterior
        self.entradas[tipo] = {'f': freq_var, 'comp': comp_var}
        self.resultados[tipo] = resultado_var
        self.infos[tipo] = info_var

        # --- Panel de Entrada ---
        input_frame = ttk.LabelFrame(parent_frame, text="🔢 Entrada de Datos", padding=15) # Sin style
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        # Frecuencia
        ttk.Label(input_frame, text="Frecuencia (Hz):", font=("Segoe UI", 11, "bold"), foreground="#495057").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        freq_entry = ttk.Entry(input_frame, textvariable=freq_var, font=("Segoe UI", 12))
        freq_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        freq_entry.bind("<KeyRelease>", lambda e, t=tipo: self._actualizar_calculo(t))

        # Componente (Capacitor o Inductor)
        label_texto = "Capacitancia (F):" if tipo == 'capacitiva' else "Inductancia (H):"
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
        """Convierte un string a float, devolviendo None si está vacío o es inválido."""
        if not value_str.strip():
            return None
        try:
            return float(value_str.strip().replace(',', '.'))
        except ValueError:
            return None # Indicar valor inválido

    def _actualizar_calculo(self, tipo: str, event=None):
        """Calcula la reactancia para la pestaña activa."""
        try:
            freq_var = self.entradas[tipo]['f']
            comp_var = self.entradas[tipo]['comp']
            resultado_var = self.resultados[tipo]
            info_var = self.infos[tipo]

            f_str = freq_var.get()
            comp_str = comp_var.get()

            f = self._parse_float(f_str)
            comp = self._parse_float(comp_str)

            # Verificar si hay texto inválido en campos no vacíos
            campos_con_texto = sum(1 for txt in [f_str, comp_str] if txt.strip())
            valores_validos = sum(1 for val in [f, comp] if val is not None)

            if campos_con_texto > valores_validos:
                 resultado_var.set("Error")
                 info_var.set("Por favor, ingrese solo números válidos.")
                 return

            if f is not None and comp is not None:
                # Tenemos ambos valores, intentar calcular
                try:
                    if tipo == 'capacitiva':
                        xc = calcular_reactancia_capacitiva(f, comp)
                        resultado = formatear_valor(xc, 'Ω')
                        formula = "Xc = 1 / (2 * π * f * C)"
                        unidad_comp = "F"
                    else: # tipo == 'inductiva'
                        xl = calcular_reactancia_inductiva(f, comp)
                        resultado = formatear_valor(xl, 'Ω')
                        formula = "Xl = 2 * π * f * L"
                        unidad_comp = "H"

                    resultado_var.set(f"Reactancia = {resultado}")
                    info_var.set(f"Calculado con f={formatear_valor(f, 'Hz')} y {'C' if tipo=='capacitiva' else 'L'}={formatear_valor(comp, unidad_comp)}. Fórmula: {formula}")

                except ValueError as e:
                    # Capturar errores de la lógica (ej. f<=0, C<=0)
                    resultado_var.set("Error")
                    info_var.set(str(e))
            else:
                # No hay suficientes datos
                resultado_var.set("")
                info_var.set("Ingrese Frecuencia y Valor del Componente.")

        except KeyError:
             # Error si el 'tipo' no coincide con las claves de los diccionarios
             print(f"Error interno: tipo de reactancia '{tipo}' no reconocido.")
        except Exception as e:
            # Capturar cualquier otro error inesperado
            try:
                self.resultados[tipo].set("Error")
                self.infos[tipo].set(f"Error inesperado: {e}")
            except KeyError:
                print(f"Error inesperado al intentar mostrar error para tipo '{tipo}': {e}")


    def _limpiar_campos(self, tipo: str):
        """Limpia los campos de la pestaña especificada."""
        try:
            self.entradas[tipo]['f'].set("")
            self.entradas[tipo]['comp'].set("")
            self.resultados[tipo].set("")
            self.infos[tipo].set("Ingrese Frecuencia y Valor del Componente.")
        except KeyError:
             print(f"Error interno: tipo de reactancia '{tipo}' no reconocido al limpiar.")
