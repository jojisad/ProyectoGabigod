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

		head = ttk.Frame(self)
		head.pack(fill=tk.X)
		title = ttk.Label(head, text="Calculadora: Código de colores", font=("Segoe UI", 16, "bold"))
		title.pack(side=tk.LEFT, padx=10, pady=12)
		if on_back:
			btn_back = ttk.Button(head, text="⟵ Volver al menú", command=on_back)
			btn_back.pack(side=tk.RIGHT, padx=10)

		controls = ttk.Frame(self)
		controls.pack(fill=tk.X, padx=10)

		# Selector de número de bandas
		ttk.Label(controls, text="Bandas:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
		for i, n in enumerate((4, 5, 6), start=1):
			ttk.Radiobutton(controls, text=str(n), variable=self.band_count_var, value=n, command=self._rebuild_bands).grid(row=0, column=i, padx=2)

		self.bands_frame = ttk.Frame(self)
		self.bands_frame.pack(fill=tk.X, padx=10, pady=6)

		# Canvas para previsualizar la resistencia
		self.canvas = tk.Canvas(self, height=140, bg="#fafafa", highlightthickness=1, highlightbackground="#ddd")
		self.canvas.pack(fill=tk.X, padx=10, pady=10)
		self.canvas.bind("<Configure>", lambda e: self._draw_resistor([v.get() for v in self.band_colors] if self.band_colors else ["negro","negro","negro","marrón"]))

		# Resultado
		self.result_var = tk.StringVar(value="")
		self.detail_var = tk.StringVar(value="")
		result_frame = ttk.Frame(self)
		result_frame.pack(fill=tk.X, padx=10, pady=6)
		ttk.Label(result_frame, text="Resultado:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
		self.result_label = ttk.Label(result_frame, textvariable=self.result_var)
		self.result_label.pack(side=tk.LEFT, padx=8)
		self.detail_label = ttk.Label(self, textvariable=self.detail_var)
		self.detail_label.pack(fill=tk.X, padx=10)

		self._rebuild_bands()
		# Forzar un primer dibujo con 4 bandas por defecto
		self.after(10, self._update_result)

	def _rebuild_bands(self) -> None:
		for child in self.bands_frame.winfo_children():
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

		for idx, role in enumerate(roles):
			var = tk.StringVar()
			self.band_colors.append(var)
			frame = ttk.Frame(self.bands_frame)
			frame.grid(row=0, column=idx, padx=4)
			label = ttk.Label(frame, text=f"Banda {idx+1}\n({role})")
			label.pack()
			combo = ttk.Combobox(frame, textvariable=var, state="readonly", width=10)
			combo["values"] = self._colors_for_role(role)
			combo.bind("<<ComboboxSelected>>", lambda e: self._update_result())
			combo.current(0)
			combo.pack()

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
		bands = [v.get() for v in self.band_colors]
		if any(b == "" for b in bands):
			return
		try:
			value, tol, ppm = calcular_resistencia_por_bandas(bands)
			self.result_var.set(formatear_ohmios(value))
			detail_parts = []
			if tol is not None:
				detail_parts.append(f"±{tol}%")
			if ppm is not None:
				detail_parts.append(f"{ppm} ppm/°C")
			self.detail_var.set("  ".join(detail_parts))
			self._draw_resistor(bands)
		except Exception as exc:
			self.result_var.set("Error")
			self.detail_var.set(str(exc))

	def _draw_resistor(self, bands: List[str]) -> None:
		self.canvas.delete("all")
		w = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
		h = self.canvas.winfo_height()
		margin = 40
		body_w = w - 2 * margin
		body_h = 60
		y = h // 2
		# terminales
		self.canvas.create_line(margin - 30, y, margin, y, width=6, fill="#999")
		self.canvas.create_line(w - margin, y, w - margin + 30, y, width=6, fill="#999")
		# cuerpo
		self.canvas.create_rectangle(margin, y - body_h // 2, margin + body_w, y + body_h // 2, fill="#f2f2f2", outline="#cfcfcf")
		# bandas
		gap = body_w / (len(bands) + 1)
		for i, color in enumerate(bands, start=1):
			x = margin + i * gap
			self.canvas.create_rectangle(x - 8, y - body_h // 2, x + 8, y + body_h // 2, fill=self._tk_color(color), outline="")

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


