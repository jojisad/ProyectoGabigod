# calculadoras/ley_ohm_frame.py
import tkinter as tk
from tkinter import ttk
from typing import Optional

# Importamos las funciones lógicas
from logica.ley_ohm import calcular_ley_ohm, formatear_valor

class LeyOhmFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, on_back=None) -> None:
        super().__init__(master)

        # Variables para almacenar los valores de entrada y resultados
        self.voltaje_var = tk.StringVar()
        self.corriente_var = tk.StringVar()
        self.resistencia_var = tk.StringVar()
        self.resultado_var = tk.StringVar()
        self.info_var = tk.StringVar(value="Ingrese dos valores para calcular el tercero.")

        # Header con título y botón de regreso (igual que otras calculadoras)
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title = ttk.Label(header_frame, text="💡 Calculadora: Ley de Ohm (V=IR)", 
                          font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        title.pack(side=tk.LEFT)
        
        if on_back:
            btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", command=on_back)
            btn_back.pack(side=tk.RIGHT)

        # Contenedor principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- Panel de Entrada ---
        input_frame = ttk.LabelFrame(main_frame, text="🔢 Entrada de Datos", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # Configurar grid dentro del frame de entrada
        input_frame.columnconfigure(1, weight=1) # Columna de Entry se expande

        # Fila Voltaje
        ttk.Label(input_frame, text="Voltaje (V):", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        voltaje_entry = ttk.Entry(input_frame, textvariable=self.voltaje_var, font=("Segoe UI", 12))
        voltaje_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        voltaje_entry.bind("<KeyRelease>", self._actualizar_calculo) # Recalcular al escribir

        # Fila Corriente
        ttk.Label(input_frame, text="Corriente (A):", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        corriente_entry = ttk.Entry(input_frame, textvariable=self.corriente_var, font=("Segoe UI", 12))
        corriente_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        corriente_entry.bind("<KeyRelease>", self._actualizar_calculo)

        # Fila Resistencia
        ttk.Label(input_frame, text="Resistencia (Ω):", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        resistencia_entry = ttk.Entry(input_frame, textvariable=self.resistencia_var, font=("Segoe UI", 12))
        resistencia_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        resistencia_entry.bind("<KeyRelease>", self._actualizar_calculo)
        
        # Botón para limpiar entradas
        clear_button = ttk.Button(input_frame, text="Limpiar", command=self._limpiar_campos)
        clear_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # --- Panel de Resultado ---
        result_frame = ttk.LabelFrame(main_frame, text="📊 Resultado", padding=20)
        result_frame.pack(fill=tk.X)

        # Resultado principal
        result_label = ttk.Label(result_frame, textvariable=self.resultado_var, 
                                font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        result_label.pack(pady=(0, 10))

        # Información adicional
        info_label = ttk.Label(result_frame, textvariable=self.info_var, 
                              font=("Segoe UI", 10), foreground="#34495e", wraplength=600, justify=tk.CENTER)
        info_label.pack()

    def _parse_float(self, value_str: str) -> Optional[float]:
        """Convierte un string a float, devolviendo None si está vacío o es inválido."""
        if not value_str.strip():
            return None
        try:
            # Reemplazar coma por punto para soporte internacional básico
            return float(value_str.strip().replace(',', '.'))
        except ValueError:
            return None # O podrías lanzar un error específico aquí

    def _actualizar_calculo(self, event=None):
        """Intenta calcular la Ley de Ohm basado en las entradas actuales."""
        v_str = self.voltaje_var.get()
        i_str = self.corriente_var.get()
        r_str = self.resistencia_var.get()

        v = self._parse_float(v_str)
        i = self._parse_float(i_str)
        r = self._parse_float(r_str)
        
        # Contar cuántos campos tienen un valor numérico válido
        valores_validos = sum(1 for val in [v, i, r] if val is not None)
        campos_con_texto = sum(1 for txt in [v_str, i_str, r_str] if txt.strip())
        
        # Si hay texto inválido en algún campo no vacío, mostrar error
        if campos_con_texto > valores_validos:
             self.resultado_var.set("Error")
             self.info_var.set("Por favor, ingrese solo números válidos.")
             return

        if valores_validos == 2:
            try:
                v_calc, i_calc, r_calc = calcular_ley_ohm(v, i, r)
                
                # Determinar qué valor se calculó y mostrarlo
                if v is None:
                    resultado = f"Voltaje = {formatear_valor(v_calc, 'V')}"
                    info = f"Calculado con I={formatear_valor(i, 'A')} y R={formatear_valor(r, 'Ω')}"
                elif i is None:
                    resultado = f"Corriente = {formatear_valor(i_calc, 'A')}"
                    info = f"Calculado con V={formatear_valor(v, 'V')} y R={formatear_valor(r, 'Ω')}"
                else: # r is None
                    resultado = f"Resistencia = {formatear_valor(r_calc, 'Ω')}"
                    info = f"Calculado con V={formatear_valor(v, 'V')} y I={formatear_valor(i, 'A')}"
                
                self.resultado_var.set(resultado)
                self.info_var.set(info)

            except ValueError as e:
                # Mostrar errores de cálculo (ej. división por cero)
                self.resultado_var.set("Error")
                self.info_var.set(str(e))
        elif valores_validos == 3:
             self.resultado_var.set("")
             self.info_var.set("Ha ingresado los tres valores. Borre uno para calcular.")
        else: # 0 o 1 valor válido
            self.resultado_var.set("")
            self.info_var.set("Ingrese exactamente dos valores para calcular el tercero.")
            
    def _limpiar_campos(self):
        """Borra todas las entradas y resultados."""
        self.voltaje_var.set("")
        self.corriente_var.set("")
        self.resistencia_var.set("")
        self.resultado_var.set("")
        self.info_var.set("Ingrese dos valores para calcular el tercero.")