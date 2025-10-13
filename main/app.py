import tkinter as tk
from tkinter import ttk
import os
import sys

# Ensure project root is on sys.path when running as `python main/app.py`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

# Lazy imports of calculators to keep startup fast
try:
	from calculadoras.resistencia_colores import ResistenciaColoresFrame
except Exception:
	ResistenciaColoresFrame = None

try:
	from calculadoras.smd_resistencia import SMDResistenciaFrame
except Exception:
	SMDResistenciaFrame = None

try:
	from calculadoras.capacitor_smd import CalculadoraCapacitorSMD
except Exception:
	CalculadoraCapacitorSMD = None

class MultiCalcApp(tk.Tk):
	def __init__(self) -> None:
		super().__init__()
		self.title("Multi Calculadora de Resistencias")
		self.geometry("1024x700")
		self.minsize(900, 600)

		self.container = ttk.Frame(self)
		self.container.pack(fill=tk.BOTH, expand=True)

		self.frames: dict[str, tk.Frame] = {}
		self._build_menu()
		self.show_main_menu()

	def _build_menu(self) -> None:
		menubar = tk.Menu(self)
		self.config(menu=menubar)

		calculadoras_menu = tk.Menu(menubar, tearoff=False)
		calculadoras_menu.add_command(label="Menú principal", command=self.show_main_menu)
		calculadoras_menu.add_separator()
		calculadoras_menu.add_command(
			label="Código de colores (4/5/6 bandas)", command=self.show_resistencia_colores
		)
		calculadoras_menu.add_command(
			label="Código SMD (3/4 dígitos y EIA-96)", command=self.show_smd
		)
		calculadoras_menu.add_command(
			label="Capacitor SMD (3/4 dígitos y EIA-198)", command=self.show_capacitor
		)
		menubar.add_cascade(label="Calculadoras", menu=calculadoras_menu)

	def _clear_container(self) -> None:
		for child in self.container.winfo_children():
			child.destroy()

	def show_main_menu(self) -> None:
		self._clear_container()
		frame = MainMenu(self.container, on_open_colors=self.show_resistencia_colores, on_open_smd=self.show_smd)
		frame.pack(fill=tk.BOTH, expand=True)
		self.frames["main"] = frame

	def show_resistencia_colores(self) -> None:
		self._clear_container()
		if ResistenciaColoresFrame is None:
			label = ttk.Label(self.container, text="Módulo no disponible")
			label.pack(padx=16, pady=16)
			return
		frame = ResistenciaColoresFrame(self.container, on_back=self.show_main_menu)
		frame.pack(fill=tk.BOTH, expand=True)
		self.frames["res_colores"] = frame

	def show_smd(self) -> None:
		self._clear_container()
		if SMDResistenciaFrame is None:
			label = ttk.Label(self.container, text="Módulo no disponible")
			label.pack(padx=16, pady=16)
			return
		frame = SMDResistenciaFrame(self.container, on_back=self.show_main_menu)
		frame.pack(fill=tk.BOTH, expand=True)
		self.frames["smd"] = frame

	def show_capacitor(self) -> None:
		self._clear_container()
		if CalculadoraCapacitorSMD is None:
			label = ttk.Label(self.container, text="Módulo no disponible")
			label.pack(padx=16, pady=16)
			return
		frame = CalculadoraCapacitorSMD(self.container, on_back=self.show_main_menu)
		frame.pack(fill=tk.BOTH, expand=True)
		self.frames["cap_smd"] = frame


class MainMenu(ttk.Frame):
	def __init__(self, master: tk.Misc, on_open_colors, on_open_smd) -> None:
		super().__init__(master)
		self.on_open_colors = on_open_colors
		self.on_open_smd = on_open_smd

		title = ttk.Label(self, text="Multi Calculadora", font=("Segoe UI", 20, "bold"))
		title.pack(pady=20)

		desc = ttk.Label(
			self,
			text=(
				"Colección de calculadoras para proyectos electrónicos. "
				"Selecciona una opción para comenzar."
			),
			wraplength=800,
			justify=tk.CENTER,
		)
		desc.pack(pady=10)

		btns = ttk.Frame(self)
		btns.pack(pady=20)

		btn1 = ttk.Button(btns, text="Código de colores (4/5/6 bandas)", command=self.on_open_colors)
		btn1.grid(row=0, column=0, padx=10, pady=10)

		btn2 = ttk.Button(btns, text="Código SMD (3/4 dígitos y EIA-96)", command=self.on_open_smd)
		btn2.grid(row=0, column=1, padx=10, pady=10)

		# Intentar importar aquí para evitar dependencia dura
		try:
			from calculadoras.capacitor_smd import CalculadoraCapacitorSMD  # noqa: F401
			btn3 = ttk.Button(btns, text="Capacitor SMD (3/4 dígitos y EIA-198)", command=self.master.master.show_capacitor if hasattr(self.master, 'master') else None)
			btn3.grid(row=0, column=2, padx=10, pady=10)
		except Exception:
			pass


def main() -> None:
	app = MultiCalcApp()
	app.mainloop()


if __name__ == "__main__":
	main()


