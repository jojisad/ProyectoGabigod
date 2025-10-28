from typing import List, Tuple, Optional
# Reutilizamos formateador, adaptándolo si es necesario o creando uno nuevo
from .ley_ohm import formatear_valor # O crear formatear_henrios si se necesita más detalle

# Valores estándar para inductores (similares a resistencias, unidad base µH)
# Fuente común: https://www.electronics-tutorials.ws/inductors/inductor-color-code.html
VALORES_SIGNIFICATIVOS_IND = {
    "negro": 0, "marrón": 1, "rojo": 2, "naranja": 3, "amarillo": 4,
    "verde": 5, "azul": 6, "violeta": 7, "gris": 8, "blanco": 9,
}

# Multiplicador (potencia de 10 para µH)
MULTIPLICADORES_IND = {
    "negro": 1,      # 10^0
    "marrón": 10,     # 10^1
    "rojo": 100,    # 10^2
    "naranja": 1_000, # 10^3
    "amarillo": 10_000,# 10^4
    "verde": 100_000,# 10^5 (raro)
    "azul": 1_000_000,# 10^6 (raro)
    "oro": 0.1,    # 10^-1
    "plata": 0.01,   # 10^-2
}

# Tolerancia (%)
TOLERANCIAS_IND = {
    "negro": 20.0, # A veces usado para 20%
    "marrón": 1.0,
    "rojo": 2.0,
    "naranja": 3.0, # Menos común
    "amarillo": 4.0, # Menos común
    "verde": 5.0, # A veces usado para 5% en lugar de oro
    "oro": 5.0,
    "plata": 10.0,
    "ninguno": 20.0 # Banda ausente
}

def calcular_inductor_por_bandas(bandas: List[str]) -> Tuple[float, Optional[float]]:
    """
    Calcula la inductancia y tolerancia de un inductor por código de colores (4 bandas).
    - Bandas: D1 D2 M T
    - Valor base en microhenrios (µH).
    - Devuelve (inductancia_en_Henrios, tolerancia_porcentaje | None).
    """
    if len(bandas) != 4:
        # Simplificamos a solo 4 bandas, el estándar más común para cálculo simple.
        # Podrían existir 3 o 5 bandas (MIL spec), pero son más complejos.
        raise ValueError("Se esperan 4 bandas de color (Dígito1, Dígito2, Multiplicador, Tolerancia).")

    try:
        d1_str, d2_str, mult_str, tol_str = bandas

        d1 = VALORES_SIGNIFICATIVOS_IND[d1_str]
        d2 = VALORES_SIGNIFICATIVOS_IND[d2_str]
        mult = MULTIPLICADORES_IND[mult_str]
        # Usamos .get() para tolerancia, ya que puede faltar o no estar en la lista simple
        tol = TOLERANCIAS_IND.get(tol_str)

        valor_uh = float(str(d1) + str(d2)) * mult

        # Convertir valor de µH a Henrios para el resultado final
        valor_h = valor_uh * 1e-6

        return valor_h, tol

    except KeyError as e:
        raise ValueError(f"Color '{e}' no reconocido para su posición en el código de inductor.") from e
    except Exception as e:
        raise ValueError(f"Error calculando inductor: {e}") from e

def formatear_henrios(valor_h: float) -> str:
    """Formatea Henrios a cadena con unidad apropiada (H, mH, µH, nH)."""
    if valor_h is None: return ""
    abs_val = abs(valor_h)
    if abs_val >= 1:
        return f"{valor_h:.3g} H"
    if abs_val >= 1e-3:
        return f"{valor_h / 1e-3:.3g} mH"
    if abs_val >= 1e-6:
        return f"{valor_h / 1e-6:.3g} µH"
    # Añadimos nano Henrios
    if abs_val >= 1e-9:
         return f"{valor_h / 1e-9:.3g} nH"
    return f"{valor_h * 1e-12:.3g} pH" # Pico Henrios si es muy pequeño
