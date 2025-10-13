import tkinter as tk
from tkinter import ttk

from logica.capacitores import (
	parsear_capacitor_eia_tres_digitos,
	parsear_capacitor_eia_cuatro_digitos,
	parsear_capacitor_eia_cuatro_mixto,
	TOLERANCIAS_EIA198,
	formatear_farads,
	formatear_mf_y_nf,
	obtener_rango_por_tolerancia,
	parsear_capacitor_eia_198,
	formatear_unidades_multiples,
)


class CalculadoraCapacitorSMD(ttk.Frame):
	def __init__(self, master: tk.Misc, on_back=None) -> None:
		super().__init__(master)
		head = ttk.Frame(self)
		head.pack(fill=tk.X)
		title = ttk.Label(head, text="Calculadora: Código de capacitor SMD", font=("Segoe UI", 16, "bold"))
		title.pack(side=tk.LEFT, padx=10, pady=12)
		if on_back:
			btn_back = ttk.Button(head, text="⟵ Volver al menú", command=on_back)
			btn_back.pack(side=tk.RIGHT, padx=10)

		# Layout principal: tabs a la izquierda, dibujo a la derecha
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True)

		left = ttk.Frame(content)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		right = ttk.Frame(content)
		right.pack(side=tk.RIGHT, fill=tk.Y)

		tabs = ttk.Notebook(left)
		tabs.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

		# Canvas de referencia del chip
		self.canvas = tk.Canvas(right, width=320, height=200, bg="#fafafa", highlightthickness=1, highlightbackground="#ddd")
		self.canvas.pack(padx=8, pady=8)
		self.canvas.bind("<Configure>", lambda e: self._redibujar_guardado())

		# Pasar callback a tabs para actualizar el dibujo
		update_cb = lambda valor, codigo, tol=None: self._actualizar_dibujo(valor, codigo, tol)

		self.tab3 = _KeypadCapTab(tabs, 3, parsear_capacitor_eia_tres_digitos, update_cb)
		self.tab4 = _KeypadCapTabMixto(tabs, update_cb)
		self.tab198 = _EIA198Tab(tabs, update_cb)

		tabs.add(self.tab3, text="EIA 3 dígitos")
		tabs.add(self.tab4, text="EIA 4 dígitos")
		tabs.add(self.tab198, text="EIA-198")

		# Estado para redibujar cuando cambie el tamaño
		self._ultimo_valor = None
		self._ultimo_codigo = ""
		self._ultima_tol = None
		self._actualizar_dibujo(None, "", None)

	def _actualizar_dibujo(self, valor_f, codigo, tol):
		# Guardar último estado
		self._ultimo_valor = valor_f
		self._ultimo_codigo = codigo
		self._ultima_tol = tol
		self.canvas.delete("all")
		w = int(self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else self.canvas.winfo_reqwidth())
		h = int(self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 200)
		cx = w // 2
		cy = h // 2
		# Dibujo simple del chip 1206
		chip_w = w - 80
		chip_h = 70
		pad_w = 30
		self.canvas.create_rectangle(cx - chip_w//2, cy - chip_h//2, cx + chip_w//2, cy + chip_h//2, fill="#202020", outline="#404040")
		# pads
		self.canvas.create_rectangle(cx - chip_w//2 - pad_w, cy - chip_h//2 + 10, cx - chip_w//2, cy + chip_h//2 - 10, fill="#c9dceb", outline="#9bb7cc")
		self.canvas.create_rectangle(cx + chip_w//2, cy - chip_h//2 + 10, cx + chip_w//2 + pad_w, cy + chip_h//2 - 10, fill="#c9dceb", outline="#9bb7cc")
		# Código impreso
		self.canvas.create_text(cx, cy, text=codigo, fill="#ffffff", font=("Segoe UI", 14, "bold"))
		# Valor formateado
		if valor_f is not None:
			texto = formatear_farads(valor_f)
			if tol is not None:
				texto += f"  (±{tol}%)"
			self.canvas.create_text(cx, cy + chip_h//2 + 20, text=texto, fill="#333")
			# Segunda línea con unidades múltiples
			self.canvas.create_text(cx, cy + chip_h//2 + 38, text=formatear_unidades_multiples(valor_f), fill="#555", font=("Segoe UI", 9))

	def _redibujar_guardado(self):
		self._actualizar_dibujo(self._ultimo_valor, self._ultimo_codigo, self._ultima_tol)



class _KeypadCapTab(ttk.Frame):
	def __init__(self, master: tk.Misc, digitos: int, parser, update_cb) -> None:
		super().__init__(master)
		self.digitos = digitos
		self.parser = parser
		self.codigo_var = tk.StringVar()
		self.resultado_var = tk.StringVar()
		self.update_cb = update_cb

		head = ttk.Frame(self)
		head.pack(fill=tk.X, padx=8, pady=6)
		ttk.Label(head, text="Código:").pack(side=tk.LEFT)
		entry = ttk.Entry(head, textvariable=self.codigo_var, width=max(6, digitos + 1))
		entry.pack(side=tk.LEFT, padx=6)
		entry.bind("<KeyRelease>", lambda e: self._actualizar())
		self.lbl_res = ttk.Label(head, textvariable=self.resultado_var, font=("Segoe UI", 11, "bold"))
		self.lbl_res.pack(side=tk.LEFT, padx=10)
		self.lbl_dual = ttk.Label(self, font=("Segoe UI", 10))
		self.lbl_dual.pack(fill=tk.X, padx=8)

		k = ttk.Frame(self)
		k.pack(padx=8, pady=8)
		botones = [str(i) for i in range(10)] + ["⌫", "Limpiar"]
		for i, label in enumerate(botones):
			btn = ttk.Button(k, text=label, width=5, command=lambda l=label: self._presionar(l))
			row = i // 6
			col = i % 6
			btn.grid(row=row, column=col, padx=2, pady=2)

		self._actualizar()

	def _presionar(self, label: str) -> None:
		texto = self.codigo_var.get()
		if label == "⌫":
			self.codigo_var.set(texto[:-1])
		elif label == "Limpiar":
			self.codigo_var.set("")
		else:
			if len(texto) < self.digitos:
				self.codigo_var.set(texto + label)
		self._actualizar()

	def _actualizar(self) -> None:
		codigo = self.codigo_var.get().strip()
		if len(codigo) != self.digitos:
			self.resultado_var.set("")
			self.update_cb(None, codigo)
			return
		try:
			valor_f = self.parser(codigo)
			self.resultado_var.set(formatear_farads(valor_f))
			self.lbl_dual.config(text=formatear_unidades_multiples(valor_f))
			self.update_cb(valor_f, codigo)
		except Exception as exc:
			self.resultado_var.set(f"Error: {exc}")
			self.update_cb(None, codigo)
class _KeypadCapTabMixto(ttk.Frame):
	def __init__(self, master: tk.Misc, update_cb) -> None:
		super().__init__(master)
		self.codigo_var = tk.StringVar()
		self.resultado_var = tk.StringVar()
		self.detalle_var = tk.StringVar()
		self.update_cb = update_cb

		head = ttk.Frame(self)
		head.pack(fill=tk.X, padx=8, pady=6)
		ttk.Label(head, text="Código (4 dígitos/letra):").pack(side=tk.LEFT)
		entry = ttk.Entry(head, textvariable=self.codigo_var, width=10)
		entry.pack(side=tk.LEFT, padx=6)
		entry.bind("<KeyRelease>", lambda e: self._actualizar())
		lbl = ttk.Label(head, textvariable=self.resultado_var, font=("Segoe UI", 11, "bold"))
		lbl.pack(side=tk.LEFT, padx=10)
		self.lbl_dual = ttk.Label(self, textvariable=self.detalle_var)
		self.lbl_dual.pack(fill=tk.X, padx=8)

		# Teclado: dígitos + R + letras de tolerancia
		panel = ttk.Frame(self)
		panel.pack(padx=8, pady=8)
		teclas = [str(i) for i in range(10)] + ["R", "B", "C", "D", "F", "G", "J", "K", "M", "Z", "⌫", "Limpiar"]
		for i, t in enumerate(teclas):
			btn = ttk.Button(panel, text=t, width=5, command=lambda c=t: self._presionar(c))
			row = i // 6
			col = i % 6
			btn.grid(row=row, column=col, padx=2, pady=2)

		self._actualizar()

	def _presionar(self, t: str) -> None:
		texto = self.codigo_var.get().upper()
		if t == "⌫":
			self.codigo_var.set(texto[:-1])
		elif t == "Limpiar":
			self.codigo_var.set("")
		else:
			if len(texto) < 4:
				self.codigo_var.set(texto + t)
		self._actualizar()

	def _actualizar(self) -> None:
		codigo = self.codigo_var.get().upper()
		if not codigo:
			self.resultado_var.set("")
			self.detalle_var.set("")
			self.update_cb(None, codigo)
			return
		try:
			valor_f, tol = parsear_capacitor_eia_cuatro_mixto(codigo)
			self.resultado_var.set(formatear_farads(valor_f))
			self.detalle_var.set(formatear_unidades_multiples(valor_f) + (f"  (±{tol}%)" if tol is not None else ""))
			self.update_cb(valor_f, codigo, tol)
		except Exception as exc:
			self.resultado_var.set(f"Error: {exc}")
			self.detalle_var.set("")
			self.update_cb(None, codigo)



class _EIA198Tab(ttk.Frame):
	def __init__(self, master: tk.Misc, update_cb) -> None:
		super().__init__(master)
		self.codigo_var = tk.StringVar()
		self.resultado_var = tk.StringVar()
		self.tol_var = tk.StringVar()
		self.update_cb = update_cb

		head = ttk.Frame(self)
		head.pack(fill=tk.X, padx=8, pady=6)
		ttk.Label(head, text="Código alfabético:").pack(side=tk.LEFT)
		entry = ttk.Entry(head, textvariable=self.codigo_var, width=8)
		entry.pack(side=tk.LEFT, padx=6)
		entry.bind("<KeyRelease>", lambda e: self._actualizar())
		self.lbl_res = ttk.Label(head, textvariable=self.resultado_var, font=("Segoe UI", 11, "bold"))
		self.lbl_res.pack(side=tk.LEFT, padx=10)

		# Panel de botones: letras EIA-198 y dígitos
		panel = ttk.Frame(self)
		panel.pack(padx=8, pady=8)
		letras = [
			"A","B","C","D","E","F","G","H","J","K","L","M","N","P","Q","R","S","T","U","V","W","X","Y","Z",
			"a","b","c","d","e","f","g","h","j","k","l","m","n","p","q","r","s","t","u","v","w","x","y","z",
		]
		for i, ch in enumerate(letras + [str(i) for i in range(10)] + ["⌫", "Limpiar"]):
			btn = ttk.Button(panel, text=ch, width=5, command=lambda c=ch: self._presionar(c))
			row = i // 6
			col = i % 6
			btn.grid(row=row, column=col, padx=2, pady=2)

		# Tolerancia letra
		fila_tol = ttk.Frame(self)
		fila_tol.pack(fill=tk.X, padx=8)
		ttk.Label(fila_tol, text="Tolerancia (letra EIA-198):").pack(side=tk.LEFT)
		combo = ttk.Combobox(fila_tol, values=list(TOLERANCIAS_EIA198.keys()), textvariable=self.tol_var, width=4, state="readonly")
		combo.pack(side=tk.LEFT, padx=6)
		combo.bind("<<ComboboxSelected>>", lambda e: self._actualizar())
		if combo["values"]:
			combo.current(0)

		self.rango_var = tk.StringVar()
		lbl_rango = ttk.Label(self, textvariable=self.rango_var)
		lbl_rango.pack(fill=tk.X, padx=8, pady=6)

		self.unidades_var = tk.StringVar()
		lbl_units = ttk.Label(self, textvariable=self.unidades_var)
		lbl_units.pack(fill=tk.X, padx=8)

		self._actualizar()

	def _presionar(self, ch: str) -> None:
		texto = self.codigo_var.get().upper()
		if ch == "⌫":
			self.codigo_var.set(texto[:-1])
		elif ch == "Limpiar":
			self.codigo_var.set("")
		else:
			nuevo = (texto + ch.upper())[:2]
			self.codigo_var.set(nuevo)
		self._actualizar()

	def _actualizar(self) -> None:
		codigo = self.codigo_var.get().strip().upper()
		if not codigo:
			self.resultado_var.set("")
			self.rango_var.set("")
			return
		try:
			if len(codigo) < 2:
				self.resultado_var.set("")
				self.rango_var.set("")
				self.update_cb(None, codigo)
				return
			valor = parsear_capacitor_eia_198(codigo[:2])
			self.resultado_var.set(formatear_farads(valor))
			tol = TOLERANCIAS_EIA198.get(self.tol_var.get())
			if tol is not None:
				vmin, vmax = obtener_rango_por_tolerancia(valor, tol)
				self.rango_var.set(f"Rango: {formatear_farads(vmin)} a {formatear_farads(vmax)} (±{tol}%)")
			else:
				self.rango_var.set("")
			self.unidades_var.set(formatear_unidades_multiples(valor))
			self.update_cb(valor, codigo, tol)
		except Exception:
			self.resultado_var.set("Código no válido")
			self.rango_var.set("")
			self.unidades_var.set("")
			self.update_cb(None, codigo)


