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

		self.tab_3d = KeypadTab(tabs, parsear_smd_eia_3_digitos, digits=3, update_cb=update_cb)
		self.tab_4d = KeypadTab(tabs, parsear_smd_eia_4_digitos, digits=4, update_cb=update_cb)
		self.tab_96 = EIA96Tab(tabs, update_cb)

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



class KeypadTab(ttk.Frame):
	def __init__(self, master: tk.Misc, parser: Callable[[str], float], digits: int, update_cb=None) -> None:
		super().__init__(master)
		self.parser = parser
		self.digits = digits
		self.value_var = tk.StringVar()
		self.result_var = tk.StringVar()
		self.update_cb = update_cb

		head = ttk.Frame(self)
		head.pack(fill=tk.X, padx=8, pady=6)
		ttk.Label(head, text="Código:").pack(side=tk.LEFT)
		entry = ttk.Entry(head, textvariable=self.value_var, width=max(6, digits + 1))
		entry.pack(side=tk.LEFT, padx=6)
		entry.bind("<KeyRelease>", lambda e: self._update())
		self.result_lbl = ttk.Label(head, textvariable=self.result_var, font=("Segoe UI", 11, "bold"))
		self.result_lbl.pack(side=tk.LEFT, padx=10)

		board = ttk.Frame(self)
		board.pack(padx=8, pady=8)
		# keypad con 0-9 y borrar
		buttons = [str(i) for i in range(10)] + ["⌫", "Limpiar"]
		for i, label in enumerate(buttons):
			cmd = (lambda l=label: self._press(l))
			btn = ttk.Button(board, text=label, width=5, command=cmd)
			row = i // 6
			col = i % 6
			btn.grid(row=row, column=col, padx=2, pady=2)

		self._update()

	def _press(self, label: str) -> None:
		text = self.value_var.get()
		if label == "⌫":
			self.value_var.set(text[:-1])
		elif label == "Limpiar":
			self.value_var.set("")
		else:
			if len(text) < self.digits:
				self.value_var.set(text + label)
		self._update()

	def _update(self) -> None:
		code = self.value_var.get().strip()
		if len(code) != self.digits:
			self.result_var.set("")
			if self.update_cb:
				self.update_cb(None, code)
			return
		try:
			value = self.parser(code)
			self.result_var.set(formatear_ohmios(value))
			if self.update_cb:
				self.update_cb(value, code)
		except Exception as exc:
			self.result_var.set(f"Error: {exc}")
			if self.update_cb:
				self.update_cb(None, code)


class EIA96Tab(ttk.Frame):
	def __init__(self, master: tk.Misc, update_cb=None) -> None:
		super().__init__(master)
		self.result_var = tk.StringVar()
		self.code_var = tk.StringVar()
		self.update_cb = update_cb

		head = ttk.Frame(self)
		head.pack(fill=tk.X, padx=8, pady=6)
		ttk.Label(head, text="Código seleccionado:").pack(side=tk.LEFT)
		code_entry = ttk.Entry(head, textvariable=self.code_var, width=6)
		code_entry.pack(side=tk.LEFT, padx=6)
		code_entry.bind("<KeyRelease>", lambda e: self._from_entry())
		self.result_lbl = ttk.Label(head, textvariable=self.result_var, font=("Segoe UI", 11, "bold"))
		self.result_lbl.pack(side=tk.LEFT, padx=10)

		board = ttk.Frame(self)
		board.pack(padx=8, pady=8)

		# botones 00-96
		for i in range(1, 97):
			code = f"{i:02d}"
			btn = ttk.Button(board, text=code, width=4, command=lambda c=code: self._pick_digits(c))
			row = (i - 1) // 12
			col = (i - 1) % 12
			btn.grid(row=row, column=col, padx=2, pady=2)

		# multiplicadores
		mult_frame = ttk.Frame(self)
		mult_frame.pack(padx=8, pady=6)
		for ch, label in ("Z", "mΩ"), ("Y", "cΩ"), ("R", "dΩ"), ("A", "Ω"), ("B", "kΩ"), ("C", "100Ω"), ("D", "kΩ"), ("E", "10kΩ"), ("F", "100kΩ"), ("H", "MΩ"):
			pass
		# Mostrar letras reales
		letters = ["Z", "Y", "R", "A", "B", "C", "D", "E", "F", "H"]
		for j, ch in enumerate(letters):
			b = ttk.Button(mult_frame, text=ch, width=3, command=lambda c=ch: self._pick_letter(c))
			b.grid(row=0, column=j, padx=2)

	def _pick_digits(self, digits: str) -> None:
		self.code_var.set(digits + (self.code_var.get()[2:] if len(self.code_var.get()) == 3 else ""))
		self._try_compute()

	def _pick_letter(self, letter: str) -> None:
		base = self.code_var.get()[:2]
		if len(base) != 2:
			return
		self.code_var.set(base + letter)
		self._try_compute()

	def _from_entry(self) -> None:
		self._try_compute()

	def _try_compute(self) -> None:
		code = self.code_var.get().strip()
		if len(code) != 3:
			self.result_var.set("")
			if self.update_cb:
				self.update_cb(None, code)
			return
		try:
			value = parsear_smd_eia_96(code)
			self.result_var.set(formatear_ohmios(value))
			if self.update_cb:
				self.update_cb(value, code)
		except Exception as exc:
			self.result_var.set(f"Error: {exc}")
			if self.update_cb:
				self.update_cb(None, code)


