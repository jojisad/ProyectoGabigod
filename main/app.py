import tkinter as tk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageTk

# Ensure project root is on sys.path when running as `python main/app.py`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

class CalculatorButton(tk.Button):
	"""Botón personalizado para calculadoras sin dinamismo"""
	def __init__(self, parent, title, description, icon, color, command=None, width=280, height=160):
		# Crear texto combinado
		button_text = f"{icon}\n\n{title}\n\n{description}"
		
		super().__init__(parent, 
			text=button_text,
			command=command,
			width=width//8,  # Ajustar para el ancho en caracteres
			height=height//20,  # Ajustar para la altura en líneas
			bg="#ffffff",
			fg="#2c3e50",
			font=("Segoe UI", 10),
			relief="solid",
			bd=2,
			wraplength=240,
			justify=tk.CENTER)
		
		# Configurar cursor
		self.configure(cursor="hand2")


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
		self.title("Multi Calculadora de Componentes Electrónicos")
		self.geometry("1200x800")
		self.minsize(1000, 700)
		
		# Configurar tema visual
		self.configure(bg="#f5f5f5")
		
		# Configurar estilo ttk
		style = ttk.Style()
		style.theme_use('clam')
		self._configurar_estilos(style)

		self.container = ttk.Frame(self, style="Main.TFrame")
		self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

		self.frames: dict[str, tk.Frame] = {}
		self._build_menu()
		self.show_main_menu()

	def _configurar_estilos(self, style):
		# Frame principal
		style.configure("Main.TFrame", background="#f5f5f5")
		
		# Botones principales
		style.configure("Main.TButton", 
			font=("Segoe UI", 12, "bold"),
			padding=(20, 15),
			background="#4a90e2",
			foreground="white",
			borderwidth=0,
			focuscolor="none")
		style.map("Main.TButton",
			background=[("active", "#357abd"), ("pressed", "#2968a3")])
		
		# Botones secundarios
		style.configure("Secondary.TButton",
			font=("Segoe UI", 10),
			padding=(15, 10),
			background="#6c757d",
			foreground="white",
			borderwidth=0)
		style.map("Secondary.TButton",
			background=[("active", "#5a6268"), ("pressed", "#495057")])
		
		# Labels de título
		style.configure("Title.TLabel",
			font=("Segoe UI", 24, "bold"),
			background="#f5f5f5",
			foreground="#2c3e50")
		
		# Labels de descripción
		style.configure("Desc.TLabel",
			font=("Segoe UI", 12),
			background="#f5f5f5",
			foreground="#6c757d")
		
		# Estilos para paneles de resultados
		style.configure("Result.TLabelFrame",
			background="#ffffff",
			borderwidth=2,
			relief="solid")
		
		style.configure("Result.TLabelFrame.Label",
			font=("Segoe UI", 12, "bold"),
			background="#ffffff",
			foreground="#2c3e50")
		
		# Estilos para entrada de datos
		style.configure("Input.TLabelFrame",
			background="#f8f9fa",
			borderwidth=1,
			relief="solid")
		
		style.configure("Input.TLabelFrame.Label",
			font=("Segoe UI", 11, "bold"),
			background="#f8f9fa",
			foreground="#495057")
		
		# Estilos para resultados principales
		style.configure("ResultMain.TLabel",
			font=("Segoe UI", 18, "bold"),
			background="#ffffff",
			foreground="#2c3e50")
		
		# Estilos para información adicional
		style.configure("ResultInfo.TLabel",
			font=("Segoe UI", 10),
			background="#ffffff",
			foreground="#7f8c8d")
		
		# Estilos para etiquetas de entrada
		style.configure("InputLabel.TLabel",
			font=("Segoe UI", 11, "bold"),
			background="#f8f9fa",
			foreground="#495057")

	def _build_menu(self) -> None:
		menubar = tk.Menu(self)
		self.config(menu=menubar)

		calculadoras_menu = tk.Menu(menubar, tearoff=False)
		calculadoras_menu.add_command(label="🏠 Menú principal", command=self.show_main_menu)
		calculadoras_menu.add_separator()
		calculadoras_menu.add_command(
			label="🎨 Código de colores (4/5/6 bandas)", command=self.show_resistencia_colores
		)
		calculadoras_menu.add_command(
			label="📱 Código SMD Resistencias (3/4 dígitos y EIA-96)", command=self.show_smd
		)
		calculadoras_menu.add_command(
			label="⚡ Capacitor SMD (3/4 dígitos y EIA-198)", command=self.show_capacitor
		)
		menubar.add_cascade(label="Calculadoras", menu=calculadoras_menu)

	def _clear_container(self) -> None:
		for child in self.container.winfo_children():
			child.destroy()

	def show_main_menu(self) -> None:
		self._clear_container()
		frame = MainMenu(self.container, 
			on_open_colors=self.show_resistencia_colores, 
			on_open_smd=self.show_smd,
			on_open_capacitor=self.show_capacitor)
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
	def __init__(self, master: tk.Misc, on_open_colors, on_open_smd, on_open_capacitor=None) -> None:
		super().__init__(master, style="Main.TFrame")
		self.on_open_colors = on_open_colors
		self.on_open_smd = on_open_smd
		self.on_open_capacitor = on_open_capacitor

		# Contenedor principal con padding
		main_container = ttk.Frame(self, style="Main.TFrame")
		main_container.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)

		# Título principal
		title_frame = ttk.Frame(main_container, style="Main.TFrame")
		title_frame.pack(fill=tk.X, pady=(0, 30))
		
		title = ttk.Label(title_frame, text="Multi Calculadora", style="Title.TLabel")
		title.pack()
		
		subtitle = ttk.Label(title_frame, text="Componentes Electrónicos", 
			font=("Segoe UI", 16), background="#f5f5f5", foreground="#7f8c8d")
		subtitle.pack(pady=(5, 0))

		# Descripción
		desc_frame = ttk.Frame(main_container, style="Main.TFrame")
		desc_frame.pack(fill=tk.X, pady=(0, 40))
		
		desc = ttk.Label(desc_frame, 
			text="Herramientas profesionales para el cálculo de resistencias y capacitores.\n"
				 "Selecciona una calculadora para comenzar.",
			style="Desc.TLabel",
			justify=tk.CENTER)
		desc.pack()

		# Grid de botones llamativos
		buttons_frame = ttk.Frame(main_container, style="Main.TFrame")
		buttons_frame.pack(expand=True, fill=tk.BOTH)
		
		# Botón 1: Resistencias por colores
		btn1_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
		btn1_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
		
		btn1 = CalculatorButton(btn1_frame, 
			title="Resistencias por Colores",
			description="Calcula el valor de resistencias mediante el código de colores estándar",
			icon="🎨",
			color="#e74c3c",
			command=self.on_open_colors)
		btn1.pack(fill=tk.BOTH, expand=True)

		# Botón 2: SMD Resistencias
		btn2_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
		btn2_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
		
		btn2 = CalculatorButton(btn2_frame,
			title="Resistencias SMD",
			description="Decodifica códigos numéricos y EIA-96 de resistencias SMD",
			icon="📱",
			color="#3498db",
			command=self.on_open_smd)
		btn2.pack(fill=tk.BOTH, expand=True)

		# Botón 3: Capacitores SMD
		try:
			from calculadoras.capacitor_smd import CalculadoraCapacitorSMD  # noqa: F401
			btn3_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
			btn3_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
			
			btn3 = CalculatorButton(btn3_frame,
				title="Capacitores SMD",
				description="Calcula valores de capacitores SMD usando códigos EIA-198",
				icon="⚡",
				color="#f39c12",
				command=self.on_open_capacitor)
			btn3.pack(fill=tk.BOTH, expand=True)
		except Exception:
			pass
		
		# Configurar grid weights
		buttons_frame.grid_columnconfigure(0, weight=1)
		buttons_frame.grid_columnconfigure(1, weight=1)
		buttons_frame.grid_columnconfigure(2, weight=1)
		buttons_frame.grid_rowconfigure(0, weight=1)


def main() -> None:
	app = MultiCalcApp()
	app.mainloop()


if __name__ == "__main__":
	main()


