import tkinter as tk
from tkinter import ttk
from typing import Callable

from logica.resistencias import (
	parsear_smd_eia_3_digitos,
	parsear_smd_eia_4_digitos,
	parsear_smd_eia_96,
	formatear_ohmios,
	formatear_ohmios_multiple,
)


class SMDResistenciaFrame(ttk.Frame):
	def __init__(self, master: tk.Misc, on_back=None) -> None:
		super().__init__(master)
		head = ttk.Frame(self)
		head.pack(fill=tk.X)
		title = ttk.Label(head, text="Calculadora: Código SMD", font=("Segoe UI", 16, "bold"))
		title.pack(side=tk.LEFT, padx=10, pady=12)
		if on_back:
			btn_back = ttk.Button(head, text="⟵ Volver al menú", command=on_back)
			btn_back.pack(side=tk.RIGHT, padx=10)

		# Layout con tabs a la izquierda y dibujo a la derecha
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True)
		left = ttk.Frame(content)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		right = ttk.Frame(content)
		right.pack(side=tk.RIGHT, fill=tk.Y)

		tabs = ttk.Notebook(left)
		tabs.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		# Canvas del chip SMD
		self.canvas = tk.Canvas(right, width=320, height=200, bg="#fafafa", highlightthickness=1, highlightbackground="#ddd")
		self.canvas.pack(padx=8, pady=8)
		self.canvas.bind("<Configure>", lambda e: self._redibujar_guardado())

		update_cb = lambda valor, codigo: self._actualizar_dibujo(valor, codigo)

		self.tab_3d = TabTeclado(tabs, parsear_smd_eia_3_digitos, digitos=3, callback_actualizacion=update_cb)
		self.tab_4d = TabTeclado(tabs, parsear_smd_eia_4_digitos, digitos=4, callback_actualizacion=update_cb)
		self.tab_96 = TabEIA96(tabs, callback_actualizacion=update_cb)

		tabs.add(self.tab_3d, text="EIA 3 dígitos")
		tabs.add(self.tab_4d, text="EIA 4 dígitos")
		tabs.add(self.tab_96, text="EIA-96")

		self._ultimo_valor = None
		self._ultimo_codigo = ""
		self._actualizar_dibujo(None, "")

	def _actualizar_dibujo(self, valor_ohms, codigo):
		self._ultimo_valor = valor_ohms
		self._ultimo_codigo = codigo
		self.canvas.delete("all")
		w = int(self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else self.canvas.winfo_reqwidth())
		h = int(self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 200)
		cx = w // 2
		cy = h // 2
		chip_w = w - 80
		chip_h = 70
		pad_w = 30
		# cuerpo y pads
		self.canvas.create_rectangle(cx - chip_w//2, cy - chip_h//2, cx + chip_w//2, cy + chip_h//2, fill="#303030", outline="#4a4a4a")
		self.canvas.create_rectangle(cx - chip_w//2 - pad_w, cy - chip_h//2 + 10, cx - chip_w//2, cy + chip_h//2 - 10, fill="#c9dceb", outline="#9bb7cc")
		self.canvas.create_rectangle(cx + chip_w//2, cy - chip_h//2 + 10, cx + chip_w//2 + pad_w, cy + chip_h//2 - 10, fill="#c9dceb", outline="#9bb7cc")
		# Código
		self.canvas.create_text(cx, cy, text=codigo, fill="#ffffff", font=("Segoe UI", 14, "bold"))
		if valor_ohms is not None:
			self.canvas.create_text(cx, cy + chip_h//2 + 20, text=formatear_ohmios(valor_ohms), fill="#333")
			self.canvas.create_text(cx, cy + chip_h//2 + 38, text=formatear_ohmios_multiple(valor_ohms), fill="#555", font=("Segoe UI", 9))

	def _redibujar_guardado(self):
		self._actualizar_dibujo(self._ultimo_valor, self._ultimo_codigo)



class TabTeclado(ttk.Frame):
	def __init__(self, master: tk.Misc, analizador: Callable[[str], float], digitos: int, callback_actualizacion=None) -> None:
		super().__init__(master)
		self.analizador = analizador
		self.digitos = digitos
		self.variable_valor = tk.StringVar()
		self.variable_resultado = tk.StringVar()
		self.callback_actualizacion = callback_actualizacion

		# Panel de entrada mejorado
		input_frame = ttk.LabelFrame(self, text="🔢 Entrada del Código", padding=15)
		input_frame.pack(fill=tk.X, padx=8, pady=6)
		
		head = ttk.Frame(input_frame)
		head.pack(fill=tk.X)
		
		ttk.Label(head, text="Código:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
		entry = ttk.Entry(head, textvariable=self.variable_valor, width=max(8, digitos + 2), 
			font=("Segoe UI", 12))
		entry.pack(side=tk.LEFT, padx=10)
		entry.bind("<KeyRelease>", lambda e: self._actualizar())
		
		# Panel de resultados mejorado
		result_frame = ttk.LabelFrame(self, text="📊 Resultado del Cálculo", padding=15)
		result_frame.pack(fill=tk.X, padx=8, pady=6)
		
		# Resultado principal
		self.etiqueta_resultado = ttk.Label(result_frame, textvariable=self.variable_resultado, 
			font=("Segoe UI", 18, "bold"), foreground="#1a1a1a")
		self.etiqueta_resultado.pack(pady=(0, 10))
		
		# Información adicional
		self.variable_info = tk.StringVar(value="")
		self.etiqueta_info = ttk.Label(result_frame, textvariable=self.variable_info, 
			font=("Segoe UI", 10), foreground="#2c3e50", wraplength=500)
		self.etiqueta_info.pack()

		panel_teclado = ttk.Frame(self)
		panel_teclado.pack(padx=8, pady=8)
		# teclado con 0-9 y borrar
		botones = [str(i) for i in range(10)] + ["⌫", "Limpiar"]
		for i, etiqueta in enumerate(botones):
			comando = (lambda l=etiqueta: self._presionar(l))
			btn = ttk.Button(panel_teclado, text=etiqueta, width=5, command=comando)
			fila = i // 6
			columna = i % 6
			btn.grid(row=fila, column=columna, padx=2, pady=2)

		self._actualizar()

	def _presionar(self, etiqueta: str) -> None:
		texto = self.variable_valor.get()
		if etiqueta == "⌫":
			self.variable_valor.set(texto[:-1])
		elif etiqueta == "Limpiar":
			self.variable_valor.set("")
		else:
			if len(texto) < self.digitos:
				self.variable_valor.set(texto + etiqueta)
		self._actualizar()

	def _actualizar(self) -> None:
		codigo = self.variable_valor.get().strip()
		if len(codigo) != self.digitos:
			self.variable_resultado.set("")
			self.variable_info.set(f"Ingresa {self.digitos} dígitos para ver el resultado")
			if self.callback_actualizacion:
				self.callback_actualizacion(None, codigo)
			return
		try:
			valor = self.analizador(codigo)
			self.variable_resultado.set(formatear_ohmios(valor))
			
			# Información adicional
			partes_info = []
			if self.digitos == 3:
				partes_info.append("Código EIA 3 dígitos: XY Z → XY × 10^Z")
			else:
				partes_info.append("Código EIA 4 dígitos: XYZ W → XYZ × 10^W")
			
			# Clasificar el valor
			if valor >= 1000000:
				partes_info.append(f"Resistencia alta: {valor/1000000:.2f} MΩ")
			elif valor >= 1000:
				partes_info.append(f"Resistencia media: {valor/1000:.2f} kΩ")
			else:
				partes_info.append(f"Resistencia baja: {valor:.2f} Ω")
			
			self.variable_info.set(" • ".join(partes_info))
			if self.callback_actualizacion:
				self.callback_actualizacion(valor, codigo)
		except Exception as exc:
			self.variable_resultado.set("Error en el cálculo")
			self.variable_info.set(f"Error: {str(exc)}")
			if self.callback_actualizacion:
				self.callback_actualizacion(None, codigo)


class TabEIA96(ttk.Frame):
	def __init__(self, master: tk.Misc, callback_actualizacion=None) -> None:
		super().__init__(master)
		self.variable_resultado = tk.StringVar()
		self.variable_codigo = tk.StringVar()
		self.callback_actualizacion = callback_actualizacion

		# Panel de entrada mejorado
		input_frame = ttk.LabelFrame(self, text="🔢 Entrada del Código EIA-96", padding=15)
		input_frame.pack(fill=tk.X, padx=8, pady=6)
		
		head = ttk.Frame(input_frame)
		head.pack(fill=tk.X)
		
		ttk.Label(head, text="Código:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
		entry_codigo = ttk.Entry(head, textvariable=self.variable_codigo, width=8, 
			font=("Segoe UI", 12))
		entry_codigo.pack(side=tk.LEFT, padx=10)
		entry_codigo.bind("<KeyRelease>", lambda e: self._desde_entrada())
		
		# Panel de resultados mejorado
		result_frame = ttk.LabelFrame(self, text="📊 Resultado del Cálculo", padding=15)
		result_frame.pack(fill=tk.X, padx=8, pady=6)
		
		# Resultado principal
		self.etiqueta_resultado = ttk.Label(result_frame, textvariable=self.variable_resultado, 
			font=("Segoe UI", 18, "bold"), foreground="#1a1a1a")
		self.etiqueta_resultado.pack(pady=(0, 10))
		
		# Información adicional
		self.variable_info = tk.StringVar(value="")
		self.etiqueta_info = ttk.Label(result_frame, textvariable=self.variable_info, 
			font=("Segoe UI", 10), foreground="#2c3e50", wraplength=500)
		self.etiqueta_info.pack()

		panel_teclado = ttk.Frame(self)
		panel_teclado.pack(padx=8, pady=8)

		# botones 00-96
		for i in range(1, 97):
			codigo = f"{i:02d}"
			btn = ttk.Button(panel_teclado, text=codigo, width=4, command=lambda c=codigo: self._seleccionar_digitos(c))
			fila = (i - 1) // 12
			columna = (i - 1) % 12
			btn.grid(row=fila, column=columna, padx=2, pady=2)

		# multiplicadores
		marco_multiplicadores = ttk.Frame(self)
		marco_multiplicadores.pack(padx=8, pady=6)
		# Mostrar letras reales
		letras = ["Z", "Y", "R", "A", "B", "C", "D", "E", "F", "H"]
		for j, caracter in enumerate(letras):
			b = ttk.Button(marco_multiplicadores, text=caracter, width=3, command=lambda c=caracter: self._seleccionar_letra(c))
			b.grid(row=0, column=j, padx=2)

	def _seleccionar_digitos(self, digitos: str) -> None:
		self.variable_codigo.set(digitos + (self.variable_codigo.get()[2:] if len(self.variable_codigo.get()) == 3 else ""))
		self._intentar_calcular()

	def _seleccionar_letra(self, letra: str) -> None:
		base = self.variable_codigo.get()[:2]
		if len(base) != 2:
			return
		self.variable_codigo.set(base + letra)
		self._intentar_calcular()

	def _desde_entrada(self) -> None:
		self._intentar_calcular()

	def _intentar_calcular(self) -> None:
		codigo = self.variable_codigo.get().strip()
		if len(codigo) != 3:
			self.variable_resultado.set("")
			self.variable_info.set("Ingresa un código de 3 caracteres (2 dígitos + letra)")
			if self.callback_actualizacion:
				self.callback_actualizacion(None, codigo)
			return
		try:
			valor = parsear_smd_eia_96(codigo)
			self.variable_resultado.set(formatear_ohmios(valor))
			
			# Información adicional
			partes_info = []
			partes_info.append("Código EIA-96: 2 dígitos + letra multiplicador")
			
			# Mostrar desglose del código
			digitos = codigo[:2]
			letra = codigo[2]
			partes_info.append(f"Desglose: {digitos} + {letra}")
			
			# Clasificar el valor
			if valor >= 1000000:
				partes_info.append(f"Resistencia alta: {valor/1000000:.2f} MΩ")
			elif valor >= 1000:
				partes_info.append(f"Resistencia media: {valor/1000:.2f} kΩ")
			else:
				partes_info.append(f"Resistencia baja: {valor:.2f} Ω")
			
			self.variable_info.set(" • ".join(partes_info))
			if self.callback_actualizacion:
				self.callback_actualizacion(valor, codigo)
		except Exception as exc:
			self.variable_resultado.set("Error en el cálculo")
			self.variable_info.set(f"Error: {str(exc)}")
			if self.callback_actualizacion:
				self.callback_actualizacion(None, codigo)


