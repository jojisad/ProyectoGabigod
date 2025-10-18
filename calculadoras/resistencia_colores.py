import tkinter as tk
from tkinter import ttk
from typing import List

from logica.resistencias import (
	VALORES_SIGNIFICATIVOS,
	MULTIPLICADORES,
	TOLERANCIAS,
	VALORES_PPM,
	calcular_resistencia_por_bandas,
	formatear_ohmios,
)



class ResistenciaColoresFrame(ttk.Frame):
	def __init__(self, master: tk.Misc, on_back=None) -> None:
		super().__init__(master)
		self.band_count_var = tk.IntVar(value=4)
		self.band_colors: List[tk.StringVar] = []

		# Header con título y botón de regreso
		header_frame = ttk.Frame(self)
		header_frame.pack(fill=tk.X, padx=20, pady=15)
		
		title = ttk.Label(header_frame, text="🎨 Calculadora: Código de Colores", 
			font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
		title.pack(side=tk.LEFT)
		
		if on_back:
			btn_back = ttk.Button(header_frame, text="⟵ Volver al menú", 
				command=on_back)
			btn_back.pack(side=tk.RIGHT)

		# Contenedor principal
		main_frame = ttk.Frame(self)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		# Panel de controles
		controls_frame = ttk.LabelFrame(main_frame, text="Configuración", padding=15)
		controls_frame.pack(fill=tk.X, pady=(0, 15))

		# Selector de número de bandas
		bands_label = ttk.Label(controls_frame, text="Número de bandas:", 
			font=("Segoe UI", 11, "bold"))
		bands_label.pack(anchor=tk.W, pady=(0, 10))
		
		bands_frame = ttk.Frame(controls_frame)
		bands_frame.pack(fill=tk.X)
		
		for i, n in enumerate((4, 5, 6), start=1):
			radio = ttk.Radiobutton(bands_frame, text=f"{n} bandas", 
				variable=self.band_count_var, value=n, command=self._rebuild_bands)
			radio.pack(side=tk.LEFT, padx=(0, 20))

		# Panel de selección de bandas
		self.bands_panel = ttk.LabelFrame(main_frame, text="Selección de Colores", padding=15)
		self.bands_panel.pack(fill=tk.X, pady=(0, 15))

		# Canvas para previsualizar la resistencia
		canvas_frame = ttk.LabelFrame(main_frame, text="Previsualización", padding=15)
		canvas_frame.pack(fill=tk.X, pady=(0, 15))
		
		self.canvas = tk.Canvas(canvas_frame, height=160, bg="#ffffff", 
			highlightthickness=2, highlightbackground="#e0e0e0", relief="solid")
		self.canvas.pack(fill=tk.X, pady=10)
		self.canvas.bind("<Configure>", lambda e: self._draw_resistor([v.get() for v in self.band_colors] if self.band_colors else ["negro","negro","negro","marrón"]))

		# Panel de resultados mejorado
		result_frame = ttk.LabelFrame(main_frame, text="📊 Resultado del Cálculo", padding=20)
		result_frame.pack(fill=tk.X)
		
		# Contenedor principal del resultado
		result_container = ttk.Frame(result_frame)
		result_container.pack(fill=tk.X)
		
		# Resultado principal con mejor diseño
		self.result_var = tk.StringVar(value="")
		result_label = ttk.Label(result_container, textvariable=self.result_var, 
			font=("Segoe UI", 20, "bold"), foreground="#1a1a1a")
		result_label.pack(pady=(0, 15))
		
		# Panel de detalles con mejor organización
		details_frame = ttk.Frame(result_container)
		details_frame.pack(fill=tk.X)
		
		# Tolerancia
		self.tolerance_var = tk.StringVar(value="")
		tolerance_label = ttk.Label(details_frame, text="Tolerancia:", 
			font=("Segoe UI", 11, "bold"), foreground="#2c3e50")
		tolerance_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
		
		self.tolerance_value_var = tk.StringVar(value="")
		tolerance_value_label = ttk.Label(details_frame, textvariable=self.tolerance_value_var, 
			font=("Segoe UI", 11), foreground="#1a1a1a")
		tolerance_value_label.grid(row=0, column=1, sticky=tk.W)
		
		# Coeficiente de temperatura (PPM)
		self.ppm_var = tk.StringVar(value="")
		ppm_label = ttk.Label(details_frame, text="Coef. Temp.:", 
			font=("Segoe UI", 11, "bold"), foreground="#2c3e50")
		ppm_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
		
		self.ppm_value_var = tk.StringVar(value="")
		ppm_value_label = ttk.Label(details_frame, textvariable=self.ppm_value_var, 
			font=("Segoe UI", 11), foreground="#1a1a1a")
		ppm_value_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
		
		# Información adicional
		self.info_var = tk.StringVar(value="")
		info_label = ttk.Label(result_container, textvariable=self.info_var, 
			font=("Segoe UI", 10), foreground="#2c3e50", wraplength=600)
		info_label.pack(pady=(15, 0))

		self._rebuild_bands()
		# Forzar un primer dibujo con 4 bandas por defecto
		self.after(10, self._update_result)

	def _rebuild_bands(self) -> None:
		# Limpiar panel anterior
		for child in self.bands_panel.winfo_children():
			child.destroy()
		self.band_colors.clear()

		band_count = self.band_count_var.get()
		# Definir roles por posición
		roles = []
		if band_count == 4:
			roles = ["d", "d", "m", "t"]
		elif band_count == 5:
			roles = ["d", "d", "d", "m", "t"]
		else:
			roles = ["d", "d", "d", "m", "t", "ppm"]

		# Crear grid de selección
		for idx, role in enumerate(roles):
			var = tk.StringVar()
			self.band_colors.append(var)
			
			band_frame = ttk.Frame(self.bands_panel)
			band_frame.grid(row=0, column=idx, padx=10, pady=5, sticky="nsew")
			
			# Etiqueta de la banda
			role_names = {"d": "Dígito", "m": "Multiplicador", "t": "Tolerancia", "ppm": "PPM"}
			label = ttk.Label(band_frame, text=f"Banda {idx+1}\n({role_names[role]})", 
				font=("Segoe UI", 10, "bold"), justify=tk.CENTER)
			label.pack(pady=(0, 5))
			
			# Combo de colores
			combo = ttk.Combobox(band_frame, textvariable=var, state="readonly", 
				width=12)
			combo["values"] = self._colors_for_role(role)
			combo.bind("<<ComboboxSelected>>", lambda e: self._update_result())
			combo.current(0)
			combo.pack()
			
			# Configurar grid weights
			self.bands_panel.grid_columnconfigure(idx, weight=1)

		self._update_result()

	def _colors_for_role(self, role: str):
		if role == "d":
			return list(VALORES_SIGNIFICATIVOS.keys())
		if role == "m":
			return list(MULTIPLICADORES.keys())
		if role == "t":
			return list(TOLERANCIAS.keys())
		if role == "ppm":
			return list(VALORES_PPM.keys())
		return []

	def _update_result(self) -> None:
		bands = [v.get() for v in self.band_colors if v.get()]
		if len(bands) != len(self.band_colors):
			self.result_var.set("")
			self.tolerance_var.set("")
			self.tolerance_value_var.set("")
			self.ppm_var.set("")
			self.ppm_value_var.set("")
			self.info_var.set("Selecciona todos los colores para ver el resultado")
			self._draw_resistor(bands)
			return
		try:
			value, tol, ppm = calcular_resistencia_por_bandas(bands)
			self.result_var.set(formatear_ohmios(value))
			
			# Actualizar tolerancia
			if tol is not None:
				self.tolerance_var.set("Tolerancia:")
				self.tolerance_value_var.set(f"±{tol}%")
			else:
				self.tolerance_var.set("")
				self.tolerance_value_var.set("")
			
			# Actualizar PPM
			if ppm is not None:
				self.ppm_var.set("Coef. Temp.:")
				self.ppm_value_var.set(f"{ppm} ppm/°C")
			else:
				self.ppm_var.set("")
				self.ppm_value_var.set("")
			
			# Información adicional
			band_count = self.band_count_var.get()
			info_parts = []
			if band_count == 4:
				info_parts.append("Resistencia de 4 bandas: 2 dígitos + multiplicador + tolerancia")
			elif band_count == 5:
				info_parts.append("Resistencia de 5 bandas: 3 dígitos + multiplicador + tolerancia")
			else:
				info_parts.append("Resistencia de 6 bandas: 3 dígitos + multiplicador + tolerancia + coeficiente de temperatura")
			
			# Agregar información sobre el valor
			if value >= 1000000:
				info_parts.append(f"Valor alto: {value/1000000:.2f} MΩ")
			elif value >= 1000:
				info_parts.append(f"Valor medio: {value/1000:.2f} kΩ")
			else:
				info_parts.append(f"Valor bajo: {value:.2f} Ω")
			
			# Agregar conversión múltiple
			from logica.resistencias import formatear_ohmios_multiple
			info_parts.append(formatear_ohmios_multiple(value))
			
			self.info_var.set(" • ".join(info_parts))
			self._draw_resistor(bands)
		except Exception as exc:
			self.result_var.set("Error en el cálculo")
			self.tolerance_var.set("")
			self.tolerance_value_var.set("")
			self.ppm_var.set("")
			self.ppm_value_var.set("")
			self.info_var.set(f"Error: {str(exc)}")
			self._draw_resistor(bands)

	def _draw_resistor(self, bands: List[str]) -> None:
		self.canvas.delete("all")
		w = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
		h = self.canvas.winfo_height()
		margin = 40
		body_w = w - 2 * margin
		body_h = 80
		y = h // 2
		
		# Terminales (más gruesas y elegantes)
		self.canvas.create_line(margin - 35, y, margin, y, width=8, fill="#666", capstyle="round")
		self.canvas.create_line(w - margin, y, w - margin + 35, y, width=8, fill="#666", capstyle="round")
		
		# Cuerpo principal (más elegante)
		self.canvas.create_rectangle(margin, y - body_h // 2, margin + body_w, y + body_h // 2, 
			fill="#f8f9fa", outline="#dee2e6", width=2)
		
		# Bandas (más definidas)
		if bands and len(bands) > 0:
			gap = body_w / (len(bands) + 1)
			for i, color in enumerate(bands, start=1):
				x = margin + i * gap
				band_color = self._tk_color(color)
				# Banda principal
				self.canvas.create_rectangle(x - 10, y - body_h // 2, x + 10, y + body_h // 2, 
					fill=band_color, outline="#333", width=1)

	def _tk_color(self, nombre: str) -> str:
		# Colores aproximados
		mapa = {
			"negro": "#000000",
			"marrón": "#8B4513",
			"rojo": "#C00000",
			"naranja": "#FF8C00",
			"amarillo": "#FFD700",
			"verde": "#228B22",
			"azul": "#1E90FF",
			"violeta": "#800080",
			"gris": "#808080",
			"blanco": "#FFFFFF",
			"oro": "#D4AF37",
			"plata": "#C0C0C0",
			"rosa": "#FFC0CB",
		}
		return mapa.get(nombre, "#000000")


