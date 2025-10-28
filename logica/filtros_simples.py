import math
from typing import Optional
# Reutilizamos formateador
from .ley_ohm import formatear_valor

def calcular_fc_filtro_rc(resistencia: float, capacitancia: float) -> float:
    """
    Calcula la Frecuencia de Corte (Fc) para un filtro RC simple (paso bajo o paso alto).
    Fc = 1 / (2 * pi * R * C)
    resistencia (R) en Ohmios (Ω).
    capacitancia (C) en Faradios (F).
    Devuelve Fc en Hertz (Hz).
    Lanza ValueError si R <= 0 o C <= 0.
    """
    if resistencia <= 0:
        raise ValueError("La resistencia (R) debe ser mayor que cero.")
    if capacitancia <= 0:
        raise ValueError("La capacitancia (C) debe ser mayor que cero.")

    try:
        fc = 1 / (2 * math.pi * resistencia * capacitancia)
        return fc
    except ZeroDivisionError: # Aunque ya validamos, por robustez
        raise ValueError("Error de cálculo (división por cero). Verifique R y C.")
    except Exception as e:
        raise ValueError(f"Error calculando Fc para RC: {e}")

def calcular_fc_filtro_rl(resistencia: float, inductancia: float) -> float:
    """
    Calcula la Frecuencia de Corte (Fc) para un filtro RL simple (paso bajo o paso alto).
    Fc = R / (2 * pi * L)
    resistencia (R) en Ohmios (Ω).
    inductancia (L) en Henrios (H).
    Devuelve Fc en Hertz (Hz).
    Lanza ValueError si R < 0, L <= 0.
    """
    if resistencia < 0: # R puede ser 0 teóricamente, Fc=0
        raise ValueError("La resistencia (R) no puede ser negativa.")
    if inductancia <= 0:
        raise ValueError("La inductancia (L) debe ser mayor que cero.")

    try:
        # Nota: La fórmula Fc = R / (2 * pi * L) es para la frecuencia donde Xl = R.
        fc = resistencia / (2 * math.pi * inductancia)
        return fc
    except ZeroDivisionError: # Por L <= 0
        raise ValueError("Error de cálculo: La inductancia debe ser mayor que cero.")
    except Exception as e:
        raise ValueError(f"Error calculando Fc para RL: {e}")

# Usaremos formatear_valor(fc, 'Hz') para mostrar el resultado.
