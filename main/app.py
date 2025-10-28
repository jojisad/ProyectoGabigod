import tkinter as tk
from tkinter import ttk
import os
import sys
# from PIL import Image, ImageTk # PIL no se usa, comentado

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


# --- Importación de las Clases de Calculadoras ---
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

# <<< NUEVO: Importar LeyOhmFrame >>>
try:
    from calculadoras.ley_ohm_frame import LeyOhmFrame
except Exception:
    LeyOhmFrame = None
# <<< FIN NUEVO >>>
try:
    from calculadoras.divisor_voltaje_frame import DivisorVoltajeFrame
except Exception:
    DivisorVoltajeFrame = None

try:
    from calculadoras.inductor_colores_frame import InductorColoresFrame
except Exception:
    InductorColoresFrame = None

try:
    from calculadoras.reactancia_frame import ReactanciaFrame
except Exception:
    ReactanciaFrame = None

try:
    from calculadoras.filtros_simples_frame import FiltrosSimplesFrame
except Exception:
    FiltrosSimplesFrame = None

class MultiCalcApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Multi Calculadora de Componentes Electrónicos")
        # Ajustado tamaño para tercera fila de botones
        self.geometry("1200x1000")
        self.minsize(1000, 800)

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

        # Botones principales (ttk.Button, no tk.Button como CalculatorButton)
        # Este estilo puede no afectar a CalculatorButton directamente
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
        # <<< NUEVO: Añadir Ley de Ohm al menú >>>
        calculadoras_menu.add_command(
            label="💡 Ley de Ohm (V=IR)", command=self.show_ley_ohm
        )
        # <<< FIN NUEVO >>>
        calculadoras_menu.add_command(
            label="🔗 Divisor de Voltaje", command=self.show_divisor_voltaje
        )
        calculadoras_menu.add_command(
            label="🎨 Código Colores Inductores", command=self.show_inductor_colores
        )
        calculadoras_menu.add_command(
            label="🧠 Reactancia (Xc/Xl)", command=self.show_reactancia
        )
        calculadoras_menu.add_command(
            label="✌️ Filtros RC/RL", command=self.show_filtros_simples
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
            on_open_capacitor=self.show_capacitor,
            # <<< NUEVO: Pasar la función show_ley_ohm a MainMenu >>>
            on_open_ley_ohm=self.show_ley_ohm,
            # <<< FIN NUEVO >>>
            on_open_divisor=self.show_divisor_voltaje,
            on_open_inductor=self.show_inductor_colores,
            on_open_reactancia=self.show_reactancia,
            on_open_filtros=self.show_filtros_simples
            )
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["main"] = frame

    # --- Funciones para mostrar cada calculadora ---
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

    # <<< NUEVO: Función para mostrar la calculadora Ley de Ohm >>>
    def show_ley_ohm(self) -> None:
        self._clear_container()
        if LeyOhmFrame is None:
            label = ttk.Label(self.container, text="Módulo Ley de Ohm no disponible")
            label.pack(padx=16, pady=16)
            return
        # Se crea la instancia de LeyOhmFrame
        frame = LeyOhmFrame(self.container, on_back=self.show_main_menu)
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["ley_ohm"] = frame # Opcional: guardar referencia
    # <<< FIN NUEVO >>>
    def show_divisor_voltaje(self) -> None:
        self._clear_container()
        if DivisorVoltajeFrame is None:
            label = ttk.Label(self.container, text="Módulo Divisor de Voltaje no disponible")
            label.pack(padx=16, pady=16)
            return
        frame = DivisorVoltajeFrame(self.container, on_back=self.show_main_menu)
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["divisor_voltaje"] = frame
    
    def show_inductor_colores(self) -> None:
        self._clear_container()
        if InductorColoresFrame is None:
            label = ttk.Label(self.container, text="Módulo Inductores por Colores no disponible")
            label.pack(padx=16, pady=16)
            return
        frame = InductorColoresFrame(self.container, on_back=self.show_main_menu)
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["inductor_colores"] = frame

    def show_reactancia(self) -> None:
        self._clear_container()
        if ReactanciaFrame is None:
            label = ttk.Label(self.container, text="Módulo Reactancia no disponible")
            label.pack(padx=16, pady=16)
            return
        frame = ReactanciaFrame(self.container, on_back=self.show_main_menu)
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["reactancia"] = frame
    
    def show_filtros_simples(self) -> None:
        self._clear_container()
        if FiltrosSimplesFrame is None:
            label = ttk.Label(self.container, text="Módulo Filtros Simples (Fc) no disponible")
            label.pack(padx=16, pady=16)
            return
        frame = FiltrosSimplesFrame(self.container, on_back=self.show_main_menu)
        frame.pack(fill=tk.BOTH, expand=True)
        self.frames["filtros_simples"] = frame


class MainMenu(ttk.Frame):
    # <<< MODIFICADO: Añadir on_open_ley_ohm al constructor >>>
    def __init__(self, master: tk.Misc, on_open_colors, on_open_smd, on_open_capacitor=None, on_open_ley_ohm=None, on_open_divisor=None, on_open_inductor=None, on_open_reactancia=None, on_open_filtros=None) -> None:
        super().__init__(master, style="Main.TFrame")
        self.on_open_colors = on_open_colors
        self.on_open_smd = on_open_smd
        self.on_open_capacitor = on_open_capacitor
        # <<< NUEVO: Guardar la referencia a la función >>>
        self.on_open_ley_ohm = on_open_ley_ohm
        # <<< FIN NUEVO >>>
        self.on_open_divisor = on_open_divisor
        self.on_open_inductor = on_open_inductor
        self.on_open_reactancia = on_open_reactancia
        self.on_open_filtros = on_open_filtros

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
            text="Herramientas profesionales para el cálculo de componentes electrónicos.\n"
                 "Selecciona una calculadora para comenzar.",
            style="Desc.TLabel",
            justify=tk.CENTER)
        desc.pack()

        # Grid de botones llamativos
        buttons_frame = ttk.Frame(main_container, style="Main.TFrame")
        buttons_frame.pack(expand=True, fill=tk.BOTH)

        # --- Fila 1 de Botones ---
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
        # Mantenido try-except por si falla la importación
        if self.on_open_capacitor:
            btn3_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
            btn3_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

            btn3 = CalculatorButton(btn3_frame,
                title="Capacitores SMD",
                description="Calcula valores de capacitores SMD usando códigos EIA",
                icon="⚡",
                color="#f39c12",
                command=self.on_open_capacitor)
            btn3.pack(fill=tk.BOTH, expand=True)

        # --- Fila 2 de Botones ---
        # <<< NUEVO: Botón 4: Ley de Ohm >>>
        if self.on_open_ley_ohm: # Solo crear si la función existe
             btn4_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
             # Puesto en la fila 1, columna 0
             btn4_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

             btn4 = CalculatorButton(btn4_frame,
                 title="Ley de Ohm",
                 description="Calcula Voltaje, Corriente o Resistencia (V=IR)",
                 icon="💡", # Elige un icono adecuado
                 color="#2ecc71", # Elige un color
                 command=self.on_open_ley_ohm)
             btn4.pack(fill=tk.BOTH, expand=True)
        # <<< FIN NUEVO >>>

        # <<< NUEVO: Botón 5: Divisor de Voltaje >>>
        if self.on_open_divisor:
            btn5_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
            # Puesto en la fila 1, columna 1
            btn5_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

            btn5 = CalculatorButton(btn5_frame,
                title="Divisor de Voltaje",
                description="Calcula Vout para un divisor resistivo simple",
                icon="🔗", # Elige icono
                color="#9b59b6", # Elige color
                command=self.on_open_divisor)
            btn5.pack(fill=tk.BOTH, expand=True)
        # <<< FIN NUEVO >>>

        # <<< NUEVO: Botón 6: Inductores por Colores >>>
        if self.on_open_inductor:
            btn6_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
            # Puesto en la fila 1, columna 2
            btn6_frame.grid(row=1, column=2, padx=20, pady=20, sticky="nsew")

            btn6 = CalculatorButton(btn6_frame,
                title="Inductores por Colores",
                description="Calcula inductancia usando código de 4 bandas",
                icon="🎨", # Elige icono
                color="#1abc9c", # Elige color
                command=self.on_open_inductor)
            btn6.pack(fill=tk.BOTH, expand=True)
        # <<< FIN NUEVO >>>

        # --- Fila 3 de Botones ---
        # <<< NUEVO: Botón 7: Reactancia >>>
        if self.on_open_reactancia:
            btn7_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
            # Puesto en la fila 2, columna 0
            btn7_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

            btn7 = CalculatorButton(btn7_frame,
                title="Reactancia",
                description="Calcula Xc (capacitiva) y Xl (inductiva)",
                icon="🧠", # Elige icono
                color="#e67e22", # Elige color
                command=self.on_open_reactancia)
            btn7.pack(fill=tk.BOTH, expand=True)
        # <<< FIN NUEVO >>>
        if self.on_open_filtros:
            btn8_frame = ttk.Frame(buttons_frame, style="Main.TFrame")
            # Puesto en la fila 2, columna 1
            btn8_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")

            btn8 = CalculatorButton(btn8_frame,
                title="Filtros Simples",
                description="Calcula Frecuencia de Corte (Fc) para RC y RL",
                icon="✌️", # Elige icono
                color="#34495e", # Elige color
                command=self.on_open_filtros)
            btn8.pack(fill=tk.BOTH, expand=True)
    # <<< FIN NUEVO >>>

        # (Aquí podrías añadir más botones en row=2, column=1 y row=2, column=2 si creas más calculadoras)

        # Configurar grid weights para que las columnas se expandan
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        # Configurar weights para las filas
        buttons_frame.grid_rowconfigure(0, weight=1)
        # <<< NUEVO: Añadir weight a la segunda fila si existe >>>
        buttons_frame.grid_rowconfigure(1, weight=1)
        # <<< FIN NUEVO >>>
        # <<< NUEVO: Añadir weight a la tercera fila >>>
        buttons_frame.grid_rowconfigure(2, weight=1)
        # <<< FIN NUEVO >>>


def main() -> None:
    app = MultiCalcApp()
    app.mainloop()


if __name__ == "__main__":
    main()

